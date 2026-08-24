import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from typing import Any, Optional
from context.research.domain.ports import (
    IInfrastructureFactory,
    IReportStoragePort,
    IAsyncWorkerInvokerPort,
    IResearchAgentPort,
    ILoggerPort,
    IMetricsPort,
)
from context.kit.service.rate_limiter_service import RateLimiterService
from context.kit.dtos.metadata import Metadata
from app.controllers.start_research_controller import StartResearchController
from app.controllers.get_research_status_controller import GetResearchStatusController
from app.controllers.execute_research_worker_controller import ExecuteResearchWorkerController
from context.research.application.dtos.start_research_dto import StartResearchInputDTO
from context.research.application.dtos.get_research_status_dto import GetResearchStatusInputDTO
from context.research.application.dtos.execute_research_worker_dto import ExecuteResearchWorkerInputDTO


class MockReportStorage(IReportStoragePort):
    def __init__(self):
        self.reports = {}

    def upload_report(self, job_id: str, content: str, extension: str = "md") -> str:
        key = f"reports/{job_id}.{extension}"
        self.reports[job_id] = content
        return key

    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 3600) -> str:
        return f"https://s3.amazonaws.com/test-bucket/{object_key}?signature=test"

    def report_exists(self, job_id: str, extension: str = "md") -> bool:
        return job_id in self.reports


class MockAsyncWorkerInvoker(IAsyncWorkerInvokerPort):
    def __init__(self):
        self.invocations = []

    def invoke_worker(self, job_id: str, topic: str) -> None:
        self.invocations.append({"job_id": job_id, "topic": topic})


class MockResearchAgent(IResearchAgentPort):
    def execute_research(self, topic: str) -> str:
        return f"# Report on {topic}\n\nGenerated findings..."


class MockLogger(ILoggerPort):
    def info(self, message: str, **kwargs: Any) -> None: pass
    def error(self, message: str, **kwargs: Any) -> None: pass
    def warning(self, message: str, **kwargs: Any) -> None: pass


class MockMetrics(IMetricsPort):
    def add_metric(self, name: str, unit: str, value: float) -> None: pass


class MockRateLimiter(RateLimiterService):
    def __init__(self, allow_requests: bool = True):
        self.allow_requests = allow_requests
        self.invocations = []

    def allow(self, key: str, limit: int, window_ms: int, ctx: Optional[Any] = None) -> bool:
        self.invocations.append({"key": key, "limit": limit, "window_ms": window_ms, "ctx": ctx})
        return self.allow_requests


class MockInfrastructureFactory(IInfrastructureFactory):
    def __init__(self, allow_rate_limit: bool = True):
        self.storage = MockReportStorage()
        self.invoker = MockAsyncWorkerInvoker()
        self.agent = MockResearchAgent()
        self.logger = MockLogger()
        self.metrics = MockMetrics()
        self.rate_limiter = MockRateLimiter(allow_requests=allow_rate_limit)

    def create_report_storage(self) -> IReportStoragePort: return self.storage
    def create_async_worker_invoker(self) -> IAsyncWorkerInvokerPort: return self.invoker
    def create_research_agent(self) -> IResearchAgentPort: return self.agent
    def create_logger(self) -> ILoggerPort: return self.logger
    def create_metrics(self) -> IMetricsPort: return self.metrics
    def create_rate_limiter(self) -> RateLimiterService: return self.rate_limiter


def test_start_research_controller_success():
    factory = MockInfrastructureFactory()
    controller = StartResearchController(factory=factory)

    dto = StartResearchInputDTO(topic="AI in Healthcare")
    result = controller.run(dto, ctx=Metadata(user="192.168.1.1", ip="192.168.1.1"))

    assert result.is_ok() is True
    assert result.value.status == "IN_PROGRESS"
    assert result.value.job_id is not None
    assert len(factory.invoker.invocations) == 1
    assert factory.invoker.invocations[0]["topic"] == "AI in Healthcare"
    assert len(factory.rate_limiter.invocations) == 1
    assert "start_research:192.168.1.1" in factory.rate_limiter.invocations[0]["key"]


def test_start_research_controller_rate_limit_exceeded():
    factory = MockInfrastructureFactory(allow_rate_limit=False)
    controller = StartResearchController(factory=factory)

    dto = StartResearchInputDTO(topic="AI in Healthcare")
    result = controller.run(dto, ctx=Metadata(user="192.168.1.1", ip="192.168.1.1"))

    assert result.is_err() is True
    assert result.error.err_type == "rate_limit" or result.error.code == "rate_limit"


def test_start_research_controller_validation_error():
    factory = MockInfrastructureFactory()
    controller = StartResearchController(factory=factory)

    dto = StartResearchInputDTO(topic="")
    result = controller.run(dto)

    assert result.is_err() is True
    assert result.error.err_type == "validation" or result.error.code == "VALIDATION_ERROR"


def test_get_research_status_controller_in_progress():
    factory = MockInfrastructureFactory()
    controller = GetResearchStatusController(factory=factory)

    dto = GetResearchStatusInputDTO(job_id="non-existent-job")
    result = controller.run(dto, ctx=Metadata(user="10.0.0.1", ip="10.0.0.1"))

    assert result.is_ok() is True
    assert result.value.status == "IN_PROGRESS"
    assert result.value.s3_report_url is None
    assert len(factory.rate_limiter.invocations) == 1
    assert "get_status:non-existent-job:10.0.0.1" in factory.rate_limiter.invocations[0]["key"]


def test_get_research_status_controller_rate_limit_exceeded():
    factory = MockInfrastructureFactory(allow_rate_limit=False)
    controller = GetResearchStatusController(factory=factory)

    dto = GetResearchStatusInputDTO(job_id="job-123")
    result = controller.run(dto, ctx=Metadata(user="10.0.0.1", ip="10.0.0.1"))

    assert result.is_err() is True
    assert result.error.err_type == "rate_limit" or result.error.code == "rate_limit"


def test_get_research_status_controller_completed():
    factory = MockInfrastructureFactory()
    factory.storage.reports["completed-job-123"] = "Content"
    controller = GetResearchStatusController(factory=factory)

    dto = GetResearchStatusInputDTO(job_id="completed-job-123")
    result = controller.run(dto)

    assert result.is_ok() is True
    assert result.value.status == "COMPLETED"
    assert "https://s3.amazonaws.com" in result.value.s3_report_url


def test_execute_research_worker_controller_success():
    factory = MockInfrastructureFactory()
    controller = ExecuteResearchWorkerController(factory=factory)

    dto = ExecuteResearchWorkerInputDTO(job_id="job-999", topic="Serverless Architecture")
    result = controller.run(dto)

    assert result.is_ok() is True
    assert result.value.status == "SUCCESS"
    assert result.value.s3_key == "reports/job-999.md"
    assert "job-999" in factory.storage.reports
