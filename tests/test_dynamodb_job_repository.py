import sys
import os
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.research.domain.entities.research_job import ResearchJob
from context.research.infrastructure.dynamodb_job_repository_adapter import DynamoDBJobRepositoryAdapter


def test_dynamodb_job_repository_save():
    mock_client = MagicMock()
    adapter = DynamoDBJobRepositoryAdapter(
        table_name="test-jobs-table",
        dynamo_client=mock_client
    )

    job = ResearchJob.create(topic="Serverless DDD", id="22222222-2222-2222-2222-222222222222")
    adapter.save(job)

    mock_client.put_item.assert_called_once()
    call_kwargs = mock_client.put_item.call_args[1]
    assert call_kwargs["TableName"] == "test-jobs-table"
    assert call_kwargs["Item"]["pk"]["S"] == "JOB#22222222-2222-2222-2222-222222222222"
    assert call_kwargs["Item"]["status"]["S"] == "IN_PROGRESS"


def test_dynamodb_job_repository_find_by_id_found():
    mock_client = MagicMock()
    mock_client.get_item.return_value = {
        "Item": {
            "pk": {"S": "JOB#33333333-3333-3333-3333-333333333333"},
            "id": {"S": "33333333-3333-3333-3333-333333333333"},
            "topic": {"S": "AI Agents"},
            "status": {"S": "COMPLETED"},
            "s3_key": {"S": "reports/3333.md"},
            "created_at": {"S": "2026-08-24T14:00:00"},
            "updated_at": {"S": "2026-08-24T14:01:00"}
        }
    }

    adapter = DynamoDBJobRepositoryAdapter(
        table_name="test-jobs-table",
        dynamo_client=mock_client
    )

    result = adapter.find_by_id("33333333-3333-3333-3333-333333333333")
    assert result.is_present() is True
    job = result.get()
    assert job.id.value() == "33333333-3333-3333-3333-333333333333"
    assert job.status.value == "COMPLETED"
    assert job.s3_key == "reports/3333.md"


def test_dynamodb_job_repository_find_by_id_not_found():
    mock_client = MagicMock()
    mock_client.get_item.return_value = {}

    adapter = DynamoDBJobRepositoryAdapter(
        table_name="test-jobs-table",
        dynamo_client=mock_client
    )

    result = adapter.find_by_id("non-existent-id")
    assert result.is_empty() is True

