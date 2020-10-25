from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
import json

import logging

class PostgresToS3Operator(BaseOperator):
    """
    Pull data from Postgres and uploads the results to S3

    """

    # let airflow know sql is needs to be rendered by Jinja
    template_fields = ['sql']
    template_ext = ['.sql']

    @apply_defaults
    def __init__(
            self,
            sql,
            filename,
            postgres_conn_id,
            aws_conn_id,
            bucket_name,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.aws_conn_id = aws_conn_id
        self.sql = sql
        self.filename = filename
        self.bucket_name = bucket_name

    def execute(self, context):
        postgres = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        logging.info('sql: {}'.format(self.sql))
        results = postgres.get_records(sql=self.sql) #, parameters=self.parameters
        # postgres should return a single json array (1 row, 1 col)
        assert len(results) == 1 and len(results[0]) == 1
        result = results[0][0]
        # upload to S3
        result_str = json.dumps(result)
        s3 = S3Hook(aws_conn_id=self.aws_conn_id)
        s3.load_string(
            string_data=result_str,
            key=self.filename,
            bucket_name=self.bucket_name,
            replace=True,
            encrypt=True
        )
