from app.core.config import settings, ObjectStoreProviders
from app.utils.file_repository.interface import FileRepository
from app.utils.file_repository.minio_client import MinioRepository


def get_file_repository() -> FileRepository:
    """
    Returns a file file_repository file_repository implementation.
    Can be easily switched between Minio, S3, or other implementations.
    """
    if settings.OBJECT_STORE_PROVIDER == ObjectStoreProviders.minio:
        repository = MinioRepository(
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            bucket_name=settings.MINIO_BUCKET,
            minio_url=settings.MINIO_URL,
        )
    elif settings.OBJECT_STORE_PROVIDER == ObjectStoreProviders.s3:
        raise NotImplementedError("S3 not yet implemented")
        # file_repository = S3Repository()
    return repository
