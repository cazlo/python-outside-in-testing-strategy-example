from pydantic import computed_field
from sqlmodel import SQLModel

from app.core.config import settings
from app.utils.file_repository.interface import FileRepository
from app.deps.file_repository_deps import get_file_repository
from app.models.base_uuid_model import BaseUUIDModel


class MediaBase(SQLModel):
    title: str | None = None
    description: str | None = None
    path: str | None = None


class Media(BaseUUIDModel, MediaBase, table=True):
    @computed_field
    @property
    def link(self) -> str | None:
        if self.path is None:
            return ""
        repository: FileRepository = get_file_repository()
        url = repository.get_presigned_url(
            bucket_name=settings.MINIO_BUCKET, object_name=self.path
        )
        return url
