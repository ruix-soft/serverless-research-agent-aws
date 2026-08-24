from abc import ABC, abstractmethod
from typing import Optional, Any


class ObjectStorageService(ABC):
    """
    ObjectStorageService abstrae almacenamiento en blobs (S3, GCS, MinIO).
    """

    @abstractmethod
    def presign_upload(
        self,
        key: str,
        content_type: str,
        ctx: Optional[Any] = None,
    ) -> str:
        pass

    def PresignUpload(
        self,
        ctx: Optional[Any],
        key: str,
        content_type: str,
    ) -> str:
        return self.presign_upload(key, content_type, ctx)

    @abstractmethod
    def presign_download(self, key: str, ctx: Optional[Any] = None) -> str:
        pass

    def PresignDownload(self, ctx: Optional[Any], key: str) -> str:
        return self.presign_download(key, ctx)

    @abstractmethod
    def delete(self, key: str, ctx: Optional[Any] = None) -> None:
        pass

    def Delete(self, ctx: Optional[Any], key: str) -> None:
        self.delete(key, ctx)

