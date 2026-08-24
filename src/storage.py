import os
import boto3
from botocore.exceptions import ClientError

class S3ReportStorage:
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv("REPORTS_BUCKET_NAME", "serverless-research-agent-reports-bucket")
        self.s3_client = boto3.client("s3")

    def upload_report(self, job_id: str, content: str, extension: str = "md") -> str:
        """Subes el contenido del reporte a S3 en la ruta 'reports/'."""
        object_key = f"reports/{job_id}.{extension}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content.encode("utf-8"),
                ContentType="text/markdown; charset=utf-8"
            )
            return object_key
        except ClientError as e:
            raise RuntimeError(f"Error al subir el reporte a S3: {str(e)}")

    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 3600) -> str:
        """Genera una URL presignada con expiración para acceso temporal seguro."""
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key
                },
                ExpiresIn=expiration_seconds
            )
        except ClientError as e:
            raise RuntimeError(f"Error generando la Presigned URL: {str(e)}")