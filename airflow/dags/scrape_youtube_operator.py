# import pandas as pd
import json
import googleapiclient.discovery
import googleapiclient.errors

from airflow.hooks.S3_hook import S3Hook
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

import logging

class ScrapeYoutubeAPIOperator(BaseOperator):
    """
    Get playlist data from Youtube API and upload the results to S3

    """

    @apply_defaults
    def __init__(
            self,
            playlist_id,
            filename,
            youtube_api_key,
            aws_conn_id,
            bucket_name,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.bucket_name = bucket_name
        self.filename = filename
        self.playlist_id = playlist_id
        self.youtube_api_key = youtube_api_key

    def execute(self, context):
        logging.info('Building Youtube API...')
        youtube_service = googleapiclient.discovery.build('youtube', 'v3', developerKey=self.youtube_api_key, cache_discovery=False)
        logging.info('done')

        pl_page_token = None
        vid_page_token = None
        all_items_returned = False
        results = []
        prev_video_ids = ''
        logging.info('Downloading data via API...')
        while not all_items_returned:
            request = youtube_service.playlistItems().list(
                part='contentDetails',
                playlistId=self.playlist_id,
                maxResults=50,
                pageToken=pl_page_token
            )
            response = request.execute()
            if 'nextPageToken' in response:
                pl_page_token = response['nextPageToken']
            else:
                all_items_returned = True
            video_ids = ','.join([item['contentDetails']['videoId'] for item in response['items'] if item['contentDetails']['videoId'] not in prev_video_ids])
            prev_video_ids = prev_video_ids + video_ids + ','
            video_request = youtube_service.videos().list(
                part='contentDetails,id,player,snippet,statistics,topicDetails',
                id=video_ids,
                maxResults=50,
                pageToken=vid_page_token
            )
            video_response = video_request.execute()
            current_page_results = [{
                'id': item['id'],
                'publishedAt': item['snippet']['publishedAt'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'categoryId': item['snippet']['categoryId'],
                'duration': item['contentDetails']['duration'],
                'definition': item['contentDetails']['definition'],
                'viewCount': item['statistics']['viewCount'],
                'likeCount': item['statistics']['likeCount'],
                'dislikeCount': None,  # Youtube API no longer provides this field https://developers.google.com/youtube/v3/revision_history#december-15,-2021
                'favoriteCount': item['statistics']['favoriteCount'],
                'commentCount': item['statistics']['commentCount'],
                'embedHtml': item['player']['embedHtml']
                } for item in video_response['items']]
            results.extend(current_page_results)
            if 'nextPageToken' in video_response:
                vid_page_token = video_response['nextPageToken']

        logging.info('done')
        # TODO why are there only 811 results from video list response?

        # load scrape results to s3
        logging.info('Dumping results...')

        result_str = json.dumps(results)
        s3 = S3Hook(aws_conn_id=self.aws_conn_id)
        s3.load_string(
            string_data=result_str,
            key=self.filename,
            bucket_name=self.bucket_name,
            replace=True,
            encrypt=True
        )

        logging.info('done, exiting')
        