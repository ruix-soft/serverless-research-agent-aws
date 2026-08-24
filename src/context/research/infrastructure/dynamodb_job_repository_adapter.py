import os
import time
from typing import Optional, Any, Dict
import boto3
from botocore.exceptions import ClientError
from context.kit.dtos.optional import Optional as KitOptional
from context.research.domain.entities.research_job import ResearchJob
from context.research.domain.ports import IResearchJobRepository


class DynamoDBJobRepositoryAdapter(IResearchJobRepository):
    """
    DynamoDB adapter implementing IResearchJobRepository for persisting and querying ResearchJob aggregates.
    """

    def __init__(
        self,
        table_name: Optional[str] = None,
        dynamo_client: Optional[Any] = None,
        region_name: Optional[str] = None,
    ) -> None:
        self._table_name = table_name or os.getenv(
            "JOBS_TABLE_NAME",
            "serverless-research-agent-jobs"
        )
        self._region = region_name or os.getenv(
            "AWS_REGION",
            os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        self._dynamo_client = dynamo_client or boto3.client(
            "dynamodb",
            region_name=self._region
        )

    def save(self, job: ResearchJob) -> None:
        """Persists or updates a ResearchJob aggregate root in DynamoDB."""
        ttl_seconds = int(time.time()) + (7 * 24 * 3600)  # 7-day retention
        item: Dict[str, Any] = {
            "pk": {"S": f"JOB#{job.id.value()}"},
            "id": {"S": job.id.value()},
            "topic": {"S": job.topic.value()},
            "status": {"S": job.status.value},
            "created_at": {"S": str(job.created_at)},
            "updated_at": {"S": str(job.updated_at)},
            "expires_at": {"N": str(ttl_seconds)},
        }
        if job.s3_key:
            item["s3_key"] = {"S": job.s3_key}
        if job.error_message:
            item["error_message"] = {"S": job.error_message}

        try:
            self._dynamo_client.put_item(
                TableName=self._table_name,
                Item=item
            )
        except ClientError as e:
            raise RuntimeError(f"Error guardando ResearchJob en DynamoDB: {str(e)}") from e

    def find_by_id(self, job_id: str) -> KitOptional[ResearchJob]:
        """Retrieves a ResearchJob aggregate root by job_id from DynamoDB."""
        pk = f"JOB#{job_id}" if not job_id.startswith("JOB#") else job_id

        try:
            response = self._dynamo_client.get_item(
                TableName=self._table_name,
                Key={"pk": {"S": pk}}
            )
            item = response.get("Item")
            if not item:
                # Also try querying by raw job_id without prefix if not found
                if pk.startswith("JOB#"):
                    raw_pk = pk.replace("JOB#", "")
                    alt_resp = self._dynamo_client.get_item(
                        TableName=self._table_name,
                        Key={"pk": {"S": raw_pk}}
                    )
                    item = alt_resp.get("Item")

            if not item:
                return KitOptional.empty()

            raw_id = item.get("id", {}).get("S") or pk.replace("JOB#", "")
            data: Dict[str, Any] = {
                "id": raw_id,
                "topic": item.get("topic", {}).get("S", "Research Task"),
                "status": item.get("status", {}).get("S", "IN_PROGRESS"),
            }
            if "s3_key" in item:
                data["s3_key"] = item["s3_key"]["S"]
            if "error_message" in item:
                data["error_message"] = item["error_message"]["S"]
            if "created_at" in item:
                data["created_at"] = item["created_at"]["S"]
            if "updated_at" in item:
                data["updated_at"] = item["updated_at"]["S"]

            return KitOptional.of(ResearchJob.from_primitives(data))
        except ClientError as e:
            raise RuntimeError(f"Error consultando ResearchJob en DynamoDB: {str(e)}") from e

