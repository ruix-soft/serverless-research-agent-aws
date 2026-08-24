import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app.aws.handlers.start_research_handler import lambda_handler as start_handler
from app.aws.handlers.get_research_status_handler import lambda_handler as status_handler
from app.aws.handlers.execute_research_worker_handler import lambda_handler as worker_handler
from context.kit.dtos.result import Result
from context.kit.errors.rate_limit_error import new_rate_limit_error
from context.research.application.dtos.start_research_dto import StartResearchOutputDTO
from context.research.application.dtos.get_research_status_dto import GetResearchStatusOutputDTO
from context.research.application.dtos.execute_research_worker_dto import ExecuteResearchWorkerOutputDTO


class DummyLambdaContext:
    function_name = "test_func"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:mx-central-1:123456789012:function:test_func"
    aws_request_id = "test-request-id-123"


def test_start_research_handler_missing_topic():
    event = {"body": "{}"}
    context = DummyLambdaContext()
    response = start_handler(event, context)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["code"] == "VALIDATION_ERROR" or body.get("type") == "validation"


def test_start_research_handler_malformed_json():
    event = {"body": "{ malformed json"}
    context = DummyLambdaContext()
    response = start_handler(event, context)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body["code"] == "BAD_REQUEST" or body.get("type") == "bad_request"


@patch("app.aws.handlers.start_research_handler._controller.run")
def test_start_research_handler_success(mock_run):
    mock_run.return_value = Result.ok(
        StartResearchOutputDTO(
            job_id="job-123",
            status="IN_PROGRESS",
            message="Investigación iniciada.",
            status_url="/research/job-123"
        )
    )

    event = {
        "body": json.dumps({"topic": "Serverless Architecture", "depth": "detailed"}),
        "requestContext": {
            "identity": {"sourceIp": "192.168.1.50"},
            "requestId": "req-123"
        }
    }
    context = DummyLambdaContext()
    response = start_handler(event, context)

    assert response["statusCode"] == 202
    body = json.loads(response["body"])
    assert body["job_id"] == "job-123"
    assert body["status"] == "IN_PROGRESS"


@patch("app.aws.handlers.start_research_handler._controller.run")
def test_start_research_handler_rate_limit(mock_run):
    mock_run.return_value = Result.err(
        new_rate_limit_error(key="start_research:192.168.1.50", limit=5, window_ms=60000)
    )

    event = {
        "body": json.dumps({"topic": "AI in Cloud"}),
        "requestContext": {
            "identity": {"sourceIp": "192.168.1.50"},
            "requestId": "req-123"
        }
    }
    context = DummyLambdaContext()
    response = start_handler(event, context)

    assert response["statusCode"] == 429
    body = json.loads(response["body"])
    assert body.get("type") == "rate_limit" or body.get("code") == "rate_limit"


def test_get_research_status_handler_missing_param():
    event = {"pathParameters": None}
    context = DummyLambdaContext()
    response = status_handler(event, context)

    assert response["statusCode"] == 400


@patch("app.aws.handlers.get_research_status_handler._controller.run")
def test_get_research_status_handler_success(mock_run):
    mock_run.return_value = Result.ok(
        GetResearchStatusOutputDTO(
            job_id="job-123",
            status="COMPLETED",
            s3_report_url="https://s3.amazonaws.com/test-bucket/reports/job-123.md"
        )
    )

    event = {
        "pathParameters": {"job_id": "job-123"},
        "requestContext": {
            "identity": {"sourceIp": "10.0.0.1"},
            "requestId": "req-456"
        }
    }
    context = DummyLambdaContext()
    response = status_handler(event, context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "COMPLETED"
    assert "https://s3.amazonaws.com" in body["s3_report_url"]


@patch("app.aws.handlers.get_research_status_handler._controller.run")
def test_get_research_status_handler_rate_limit(mock_run):
    mock_run.return_value = Result.err(
        new_rate_limit_error(key="get_status:job-123:10.0.0.1", limit=30, window_ms=60000)
    )

    event = {
        "pathParameters": {"job_id": "job-123"},
        "requestContext": {
            "identity": {"sourceIp": "10.0.0.1"},
            "requestId": "req-456"
        }
    }
    context = DummyLambdaContext()
    response = status_handler(event, context)

    assert response["statusCode"] == 429
    body = json.loads(response["body"])
    assert body.get("type") == "rate_limit" or body.get("code") == "rate_limit"


@patch("app.aws.handlers.execute_research_worker_handler._controller.run")
def test_execute_research_worker_handler_success(mock_run):
    mock_run.return_value = Result.ok(
        ExecuteResearchWorkerOutputDTO(
            job_id="worker-job-1",
            status="SUCCESS",
            s3_key="reports/worker-job-1.md"
        )
    )

    event = {"job_id": "worker-job-1", "topic": "Robotics"}
    context = DummyLambdaContext()
    response = worker_handler(event, context)

    assert response["status"] == "SUCCESS"
    assert response["s3_key"] == "reports/worker-job-1.md"
