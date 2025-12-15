# https://github.com/Longdh57/fastapi-minio

from uuid6 import uuid7
from datetime import timedelta
from minio import Minio
from typing import BinaryIO

from .interface import FileRepository, FileResponse


class MinioRepository(FileRepository):
    """Minio implementation of the FileRepository interface"""

    def __init__(
        self, minio_url: str, access_key: str, secret_key: str, bucket_name: str
    ):
        self.minio_url = minio_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.create_bucket()

    def create_bucket(self) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name

    def get_presigned_url(self, bucket_name: str, object_name: str) -> str:
        # Request URL expired after 7 days
        url = self.client.presigned_get_object(
            bucket_name=bucket_name, object_name=object_name, expires=timedelta(days=7)
        )
        return url

    def check_file_exists(self, bucket_name: str, file_name: str) -> bool:
        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=file_name)
            return True
        except Exception as e:
            print(f"[x] Exception: {e}")
            return False

    def upload_file(
        self, file_data: BinaryIO, file_name: str, content_type: str
    ) -> FileResponse:
        try:
            object_name = f"{uuid7()}{file_name}"
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=10 * 1024 * 1024,
            )
            url = self.get_presigned_url(
                bucket_name=self.bucket_name, object_name=object_name
            )
            data_file = FileResponse(
                bucket_name=self.bucket_name, file_name=object_name, url=url
            )
            return data_file
        except Exception as e:
            raise e
