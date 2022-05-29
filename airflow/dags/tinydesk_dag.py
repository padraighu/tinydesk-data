from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from scrape_youtube_operator import ScrapeYoutubeAPIOperator
from file_to_postgres_operator import FileToPostgresOperator
from postgres_to_s3_operator import PostgresToS3Operator
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 10, 20, 0, 0, 0),
    'email': os.environ['AIRFLOW__SMTP__SMTP_USER'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}
  
dag = DAG(
    'tinydesk_pipeline',
    default_args=default_args,
    description='Load Youtube playlist data',
    template_searchpath=['/usr/local/airflow/sql'],
    schedule_interval='@daily',
    catchup=False
)

t1 = ScrapeYoutubeAPIOperator(
    task_id='get_tinydesk_video_data',
    playlist_id='PL1B627337ED6F55F0',
    youtube_api_key=os.environ['YOUTUBE_API_KEY'],
    filename='tinydesk_api_data.json',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t11 = ScrapeYoutubeAPIOperator(
    task_id='get_tinydesk_at_home_video_data',
    playlist_id='PLy2PCKGkKRVYPm1tBwoX45ocAzuhVyvJX',
    youtube_api_key=os.environ['YOUTUBE_API_KEY'],
    filename='tinydesk_at_home_api_data.json',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t2 = PostgresOperator(
    task_id='empty_staging_table',
    sql='DELETE FROM VIDEO_STAGING',
    postgres_conn_id='tinydesk_postgres',
    dag=dag
)

t13 = PostgresOperator(
    task_id='empty_staging_table_at_home',
    sql='DELETE FROM VIDEO_STAGING_AT_HOME',
    postgres_conn_id='tinydesk_postgres',
    dag=dag
)

t3 = FileToPostgresOperator(
    task_id='load_to_staging',
    filename='tinydesk_api_data.json',
    postgres_conn_id='tinydesk_postgres',
    table='video_staging',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t12 = FileToPostgresOperator(
    task_id='load_to_staging_at_home',
    filename='tinydesk_at_home_api_data.json',
    postgres_conn_id='tinydesk_postgres',
    table='video_staging_at_home',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t4 = PostgresOperator(
    task_id='load_to_final',
    sql='to_final.sql',
    postgres_conn_id='tinydesk_postgres',
    dag=dag
)
 
t5 = PostgresToS3Operator(
    task_id='top_10_viewed_to_s3',
    sql='top_videos.sql',
    params={'metric': 'VIEW_COUNT'},
    filename='tinydesk_top_10_viewed.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t6 = PostgresToS3Operator(
    task_id='top_10_commented_to_s3',
    sql='top_videos.sql',
    params={'metric': 'COMMENT_COUNT'},
    filename='tinydesk_top_10_commented.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t14 = PostgresToS3Operator(
    task_id='top_10_liked_to_s3',
    sql='top_videos.sql',
    params={'metric': 'LIKE_COUNT'},
    filename='tinydesk_top_10_liked.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t7 = PostgresToS3Operator(
    task_id='video_metrics_to_s3',
    sql='video_metrics.sql',
    params={},
    filename='tinydesk_video_metrics.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t9 = PostgresToS3Operator(
    task_id='views_by_year_to_s3',
    sql='metrics_by_year.sql',
    params={'metric': 'VIEW_COUNT'},
    filename='tinydesk_views_by_year.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t10 = PostgresToS3Operator(
    task_id='comments_by_year_to_s3',
    sql='metrics_by_year.sql',
    params={'metric': 'COMMENT_COUNT'},
    filename='tinydesk_comments_by_year.json',
    postgres_conn_id='tinydesk_postgres',
    aws_conn_id='tinydesk_aws',
    bucket_name=os.environ['S3_BUCKET'],
    dag=dag
)

t1 >> t2 >> t3

t11 >> t13 >> t12

[t3, t12] >> t4 >> [t5, t6, t7, t9, t10, t14]
