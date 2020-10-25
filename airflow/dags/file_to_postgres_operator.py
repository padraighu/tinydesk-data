from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
import json
import io

class FileToPostgresOperator(BaseOperator):
    """
    Load a JSON file (an array of JSON objects) and insert to a Postgres table. 

    """

    @apply_defaults
    def __init__(
            self,
            filename,
            postgres_conn_id,
            aws_conn_id,
            bucket_name,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.aws_conn_id = aws_conn_id
        self.filename = filename
        self.bucket_name = bucket_name

    def execute(self, context):
        # read json data from s3
        s3 = S3Hook(aws_conn_id=self.aws_conn_id)
        s3_obj = s3.get_key(
            key=self.filename,
            bucket_name=self.bucket_name
        )
        bytes_buffer = io.BytesIO()
        s3_obj.download_fileobj(bytes_buffer)
        data_str = bytes_buffer.getvalue().decode('utf-8')
        data = json.loads(data_str)

        cols = ['id', 'publishedAt', 'title', 'description', 'categoryId', 'duration', 'definition', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount', 'embedHtml']
        rows = [tuple(d[k] for k in cols) for d in data]
        # insert into target table
        postgres = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        postgres.insert_rows(
            table='video_staging',
            rows=rows
        )
