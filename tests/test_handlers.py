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
from context.kit.errors.not_found_error import new_not_found_error
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
    assert body.get("code") == "VALIDATION_ERROR" or body.get("type") == "validation"


def test_start_research_handler_malformed_json():
    event = {"body": "{ malformed json"}
    context = DummyLambdaContext()
    response = start_handler(event, context)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert body.get("code") == "BAD_REQUEST" or body.get("type") == "bad_request"


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
def test_get_research_status_handler_success_completed(mock_run):
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
def test_get_research_status_handler_success_failed(mock_run):
    mock_run.return_value = Result.ok(
        GetResearchStatusOutputDTO(
            job_id="job-999",
            status="FAILED",
            error="Bedrock timeout",
            message="Ocurrió un error al procesar la investigación."
        )
    )

    event = {
        "pathParameters": {"job_id": "job-999"},
        "requestContext": {
            "identity": {"sourceIp": "10.0.0.1"},
            "requestId": "req-456"
        }
    }
    context = DummyLambdaContext()
    response = status_handler(event, context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "FAILED"
    assert body["error"] == "Bedrock timeout"


@patch("app.aws.handlers.get_research_status_handler._controller.run")
def test_get_research_status_handler_not_found(mock_run):
    mock_run.return_value = Result.err(
        new_not_found_error("Investigación no encontrada.")
    )

    event = {
        "pathParameters": {"job_id": "non-existent"},
        "requestContext": {
            "identity": {"sourceIp": "10.0.0.1"},
            "requestId": "req-456"
        }
    }
    context = DummyLambdaContext()
    response = status_handler(event, context)

    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert body.get("type") == "not_found" or body.get("code") == "NOT_FOUND" or body.get("message") is not None


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


def test_get_research_status_handler_full_flow_with_dynamo():
    from app.aws.handlers import get_research_status_handler
    from context.research.infrastructure.dynamodb_job_repository_adapter import DynamoDBJobRepositoryAdapter
    from app.controllers.get_research_status_controller import GetResearchStatusController
    from context.research.domain.ports import IInfrastructureFactory

    mock_dynamo = MagicMock()
    mock_dynamo.get_item.return_value = {
        "Item": {
            "pk": {"S": "JOB#11111111-1111-1111-1111-111111111111"},
            "id": {"S": "11111111-1111-1111-1111-111111111111"},
            "topic": {"S": "Serverless AI"},
            "status": {"S": "IN_PROGRESS"},
            "created_at": {"S": "2026-08-24T14:00:00"},
            "updated_at": {"S": "2026-08-24T14:00:00"}
        }
    }
    mock_rate_limiter = MagicMock()
    mock_rate_limiter.allow.return_value = True

    class HandlerTestFactory(IInfrastructureFactory):
        def create_report_storage(self): return MagicMock()
        def create_job_repository(self): return DynamoDBJobRepositoryAdapter(dynamo_client=mock_dynamo)
        def create_state_machine_invoker(self): return MagicMock()
        def create_async_worker_invoker(self): return MagicMock()
        def create_research_agent(self): return MagicMock()
        def create_logger(self): return MagicMock()
        def create_metrics(self): return MagicMock()
        def create_rate_limiter(self): return mock_rate_limiter

    real_controller = GetResearchStatusController(factory=HandlerTestFactory())
    original_controller = get_research_status_handler._controller
    try:
        get_research_status_handler._controller = real_controller
        event = {
            "pathParameters": {"job_id": "11111111-1111-1111-1111-111111111111"},
            "requestContext": {
                "identity": {"sourceIp": "10.0.0.1"},
                "requestId": "req-999"
            }
        }
        context = DummyLambdaContext()
        response = status_handler(event, context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["job_id"] == "11111111-1111-1111-1111-111111111111"
        assert body["status"] == "IN_PROGRESS"
        assert body["topic"] == "Serverless AI"
    finally:
        get_research_status_handler._controller = original_controller

