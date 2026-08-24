import os
import time
from typing import Optional, Any
import boto3
from botocore.exceptions import ClientError
from context.kit.service.rate_limiter_service import RateLimiterService


class DynamoDBRateLimiterAdapter(RateLimiterService):
    """
    DynamoDB-backed Rate Limiter using atomic counter increments and TTL expiration.
    Implements a Fixed Window Counter algorithm per key and time bucket.
    """

    def __init__(
        self,
        table_name: Optional[str] = None,
        dynamo_client: Optional[Any] = None,
        region_name: Optional[str] = None,
    ) -> None:
        self._table_name = table_name or os.getenv(
            "RATE_LIMITS_TABLE_NAME",
            "serverless-research-agent-rate-limits"
        )
        self._region = region_name or os.getenv(
            "AWS_REGION",
            os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        self._dynamo_client = dynamo_client or boto3.client(
            "dynamodb",
            region_name=self._region
        )

    def allow(
        self,
        key: str,
        limit: int,
        window_ms: int,
        ctx: Optional[Any] = None,
    ) -> bool:
        """
        Determines whether an action for 'key' is permitted within 'window_ms' allowing up to 'limit' requests.
        Atomically increments 'request_count' and configures TTL for auto-cleanup.
        """
        now_ms = int(time.time() * 1000)
        window_id = now_ms // window_ms
        partition_key = f"{key}:{window_id}"
        ttl_seconds = int(time.time()) + (window_ms // 1000) + 120

        try:
            response = self._dynamo_client.update_item(
                TableName=self._table_name,
                Key={"pk": {"S": partition_key}},
                UpdateExpression="ADD request_count :inc SET expires_at = if_not_exists(expires_at, :ttl)",
                ExpressionAttributeValues={
                    ":inc": {"N": "1"},
                    ":ttl": {"N": str(ttl_seconds)},
                },
                ReturnValues="UPDATED_NEW",
            )
            request_count = int(
                response.get("Attributes", {})
                .get("request_count", {})
                .get("N", "1")
            )
            return request_count <= limit
        except ClientError as e:
            # Propagate error so decorator creates a DomainError
            raise RuntimeError(f"DynamoDB Rate Limiting failed: {str(e)}") from e

