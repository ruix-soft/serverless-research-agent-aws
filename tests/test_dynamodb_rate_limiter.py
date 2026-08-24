import sys
import os
import time
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.research.infrastructure.dynamodb_rate_limiter_adapter import DynamoDBRateLimiterAdapter


def test_dynamodb_rate_limiter_allow():
    mock_client = MagicMock()
    mock_client.update_item.return_value = {
        "Attributes": {
            "request_count": {"N": "3"}
        }
    }

    adapter = DynamoDBRateLimiterAdapter(
        table_name="test-rate-limits-table",
        dynamo_client=mock_client
    )

    allowed = adapter.allow(key="client-ip-1.2.3.4", limit=5, window_ms=60000)
    assert allowed is True

    mock_client.update_item.assert_called_once()
    call_kwargs = mock_client.update_item.call_args[1]
    assert call_kwargs["TableName"] == "test-rate-limits-table"
    assert "client-ip-1.2.3.4:" in call_kwargs["Key"]["pk"]["S"]
    assert ":inc" in call_kwargs["ExpressionAttributeValues"]
    assert ":ttl" in call_kwargs["ExpressionAttributeValues"]


def test_dynamodb_rate_limiter_reject_when_exceeded():
    mock_client = MagicMock()
    mock_client.update_item.return_value = {
        "Attributes": {
            "request_count": {"N": "6"}
        }
    }

    adapter = DynamoDBRateLimiterAdapter(
        table_name="test-rate-limits-table",
        dynamo_client=mock_client
    )

    allowed = adapter.allow(key="client-ip-1.2.3.4", limit=5, window_ms=60000)
    assert allowed is False


def test_dynamodb_rate_limiter_client_error_raises():
    mock_client = MagicMock()
    mock_client.update_item.side_effect = ClientError(
        error_response={"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
        operation_name="UpdateItem"
    )

    adapter = DynamoDBRateLimiterAdapter(
        table_name="non-existent-table",
        dynamo_client=mock_client
    )

    with pytest.raises(RuntimeError, match="DynamoDB Rate Limiting failed"):
        adapter.allow(key="client-ip-1.2.3.4", limit=5, window_ms=60000)

