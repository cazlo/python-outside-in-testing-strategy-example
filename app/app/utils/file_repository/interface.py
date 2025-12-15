from abc import ABC, abstractmethod
from typing import BinaryIO

from pydantic import BaseModel


class FileResponse(BaseModel):
    """Response model for file operations"""

    bucket_name: str
    file_name: str
    url: str


class FileRepository(ABC):
    """Abstract interface for file file_repository operations"""

    @abstractmethod
    def create_bucket(self) -> str:
        """Create a bucket if it doesn't exist"""
        pass

    @abstractmethod
    def get_presigned_url(self, bucket_name: str, object_name: str) -> str:
        """Generate a presigned URL for accessing an object"""
        pass

    @abstractmethod
    def check_file_exists(self, bucket_name: str, file_name: str) -> bool:
        """Check if a file exists in the bucket"""
        pass

    @abstractmethod
    def upload_file(
        self, file_data: BinaryIO, file_name: str, content_type: str
    ) -> FileResponse:
        """Upload a file to the file_repository and return the file information"""
        pass
