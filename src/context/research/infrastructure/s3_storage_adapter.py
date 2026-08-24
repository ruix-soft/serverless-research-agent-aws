import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from context.research.domain.ports import IReportStoragePort

class S3StorageAdapter(IReportStoragePort):
    """Adapter for AWS S3 report storage."""
    def __init__(self, s3_client=None, bucket_name: str = None):
        self._bucket_name = bucket_name or os.getenv("REPORTS_BUCKET_NAME", "serverless-research-agent-reports-bucket")
        self._region = os.getenv("AWS_REGION", "mx-central-1")
        self._s3_client = s3_client or boto3.client(
            "s3",
            region_name=self._region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"}
            )
        )

    def upload_report(self, job_id: str, content: str, extension: str = "md") -> str:
        object_key = f"reports/{job_id}.{extension}"
        try:
            self._s3_client.put_object(
                Bucket=self._bucket_name,
                Key=object_key,
                Body=content.encode("utf-8"),
                ContentType="text/markdown; charset=utf-8"
            )
            return object_key
        except ClientError as e:
            raise RuntimeError(f"Error subiendo el reporte a S3: {str(e)}")

    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 3600) -> str:
        try:
            return self._s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket_name, "Key": object_key},
                ExpiresIn=expiration_seconds
            )
        except ClientError as e:
            raise RuntimeError(f"Error generando la Presigned URL: {str(e)}")

    def report_exists(self, job_id: str, extension: str = "md") -> bool:
        object_key = f"reports/{job_id}.{extension}"
        try:
            self._s3_client.head_object(Bucket=self._bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return False
            raise RuntimeError(f"Error verificando reporte en S3: {str(e)}")

