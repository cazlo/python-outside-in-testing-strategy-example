# # S3 Repository implementation, generated not tested yet
#
# import boto3
# from uuid6 import uuid7
# from typing import BinaryIO
# from app.utils.file_repository.minio_client import FileRepository, FileResponse
#
#
# class S3Repository(FileRepository):
#     """AWS S3 implementation of the FileRepository interface"""
#
#     def __init__(
#         self,
#         aws_access_key: str,
#         aws_secret_key: str,
#         bucket_name: str,
#         region: str = "us-east-1",
#     ):
#         self.aws_access_key = aws_access_key
#         self.aws_secret_key = aws_secret_key
#         self.bucket_name = bucket_name
#         self.region = region
#         self.client = boto3.client(
#             "s3",
#             aws_access_key_id=self.aws_access_key,
#             aws_secret_access_key=self.aws_secret_key,
#             region_name=self.region,
#         )
#         self.resource = boto3.resource(
#             "s3",
#             aws_access_key_id=self.aws_access_key,
#             aws_secret_access_key=self.aws_secret_key,
#             region_name=self.region,
#         )
#         self.create_bucket()
#
#     def create_bucket(self) -> str:
#         """Create an S3 bucket if it doesn't exist"""
#         existing_buckets = self.client.list_buckets()
#         if self.bucket_name not in [
#             bucket["Name"] for bucket in existing_buckets.get("Buckets", [])
#         ]:
#             self.client.create_bucket(
#                 Bucket=self.bucket_name,
#                 CreateBucketConfiguration={"LocationConstraint": self.region}
#                 if self.region != "us-east-1"
#                 else {},
#             )
#         return self.bucket_name
#
#     def get_presigned_url(self, bucket_name: str, object_name: str) -> str:
#         """Generate a presigned URL for accessing an S3 object"""
#         url = self.client.generate_presigned_url(
#             "get_object",
#             Params={"Bucket": bucket_name, "Key": object_name},
#             ExpiresIn=7 * 24 * 60 * 60,  # 7 days in seconds
#         )
#         return url
#
#     def check_file_exists(self, bucket_name: str, file_name: str) -> bool:
#         """Check if a file exists in the S3 bucket"""
#         try:
#             self.client.head_object(Bucket=bucket_name, Key=file_name)
#             return True
#         except Exception as e:
#             print(f"[x] Exception: {e}")
#             return False
#
#     def upload_file(
#         self, file_data: BinaryIO, file_name: str, content_type: str
#     ) -> FileResponse:
#         """Upload a file to S3 and return the file information"""
#         try:
#             object_name = f"{uuid7()}{file_name}"
#             self.client.upload_fileobj(
#                 file_data,
#                 self.bucket_name,
#                 object_name,
#                 ExtraArgs={"ContentType": content_type},
#             )
#             url = self.get_presigned_url(
#                 bucket_name=self.bucket_name, object_name=object_name
#             )
#             data_file = FileResponse(
#                 bucket_name=self.bucket_name, file_name=object_name, url=url
#             )
#             return data_file
#         except Exception as e:
#             raise e
