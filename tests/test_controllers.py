import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from typing import Any, Optional, Dict
from context.research.domain.ports import (
    IInfrastructureFactory,
    IReportStoragePort,
    IResearchJobRepository,
    IStateMachineInvokerPort,
    IAsyncWorkerInvokerPort,
    IResearchAgentPort,
    ILoggerPort,
    IMetricsPort,
)
from context.kit.service.rate_limiter_service import RateLimiterService
from context.kit.dtos.optional import Optional as KitOptional
from context.kit.dtos.metadata import Metadata
from context.research.domain.entities.research_job import ResearchJob
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


class MockJobRepository(IResearchJobRepository):
    def __init__(self):
        self.jobs: Dict[str, ResearchJob] = {}

    def save(self, job: ResearchJob) -> None:
        self.jobs[job.id.value()] = job

    def find_by_id(self, job_id: str) -> KitOptional[ResearchJob]:
        if job_id in self.jobs:
            return KitOptional.of(self.jobs[job_id])
        return KitOptional.empty()


class MockStateMachineInvoker(IStateMachineInvokerPort):
    def __init__(self):
        self.invocations = []

    def start_execution(self, job_id: str, topic: str) -> None:
        self.invocations.append({"job_id": job_id, "topic": topic})


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
        self.job_repo = MockJobRepository()
        self.sfn_invoker = MockStateMachineInvoker()
        self.worker_invoker = MockAsyncWorkerInvoker()
        self.agent = MockResearchAgent()
        self.logger = MockLogger()
        self.metrics = MockMetrics()
        self.rate_limiter = MockRateLimiter(allow_requests=allow_rate_limit)

    def create_report_storage(self) -> IReportStoragePort: return self.storage
    def create_job_repository(self) -> IResearchJobRepository: return self.job_repo
    def create_state_machine_invoker(self) -> IStateMachineInvokerPort: return self.sfn_invoker
    def create_async_worker_invoker(self) -> IAsyncWorkerInvokerPort: return self.worker_invoker
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
    assert len(factory.sfn_invoker.invocations) == 1
    assert factory.sfn_invoker.invocations[0]["topic"] == "AI in Healthcare"
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
    job_id = "11111111-1111-1111-1111-111111111111"
    job = ResearchJob.create(topic="Quantum Tech", id=job_id)
    factory.job_repo.save(job)

    controller = GetResearchStatusController(factory=factory)
    dto = GetResearchStatusInputDTO(job_id=job_id)
    result = controller.run(dto, ctx=Metadata(user="10.0.0.1", ip="10.0.0.1"))

    assert result.is_ok() is True
    assert result.value.status == "IN_PROGRESS"
    assert result.value.s3_report_url is None
    assert len(factory.rate_limiter.invocations) == 1
    assert f"get_status:{job_id}:10.0.0.1" in factory.rate_limiter.invocations[0]["key"]


def test_get_research_status_controller_completed():
    factory = MockInfrastructureFactory()
    job_id = "22222222-2222-2222-2222-222222222222"
    job = ResearchJob.create(topic="AI Trends", id=job_id)
    job.mark_as_completed(f"reports/{job_id}.md")
    factory.job_repo.save(job)
    factory.storage.reports[job_id] = "Content"

    controller = GetResearchStatusController(factory=factory)
    dto = GetResearchStatusInputDTO(job_id=job_id)
    result = controller.run(dto)

    assert result.is_ok() is True
    assert result.value.status == "COMPLETED"
    assert "https://s3.amazonaws.com" in result.value.s3_report_url


def test_get_research_status_controller_failed():
    factory = MockInfrastructureFactory()
    job_id = "33333333-3333-3333-3333-333333333333"
    job = ResearchJob.create(topic="Failed Research", id=job_id)
    job.mark_as_failed("Bedrock quota exceeded")
    factory.job_repo.save(job)

    controller = GetResearchStatusController(factory=factory)
    dto = GetResearchStatusInputDTO(job_id=job_id)
    result = controller.run(dto)

    assert result.is_ok() is True
    assert result.value.status == "FAILED"
    assert result.value.error == "Bedrock quota exceeded"


def test_get_research_status_controller_not_found():
    factory = MockInfrastructureFactory()
    controller = GetResearchStatusController(factory=factory)

    dto = GetResearchStatusInputDTO(job_id="44444444-4444-4444-4444-444444444444")
    result = controller.run(dto)

    assert result.is_err() is True
    assert result.error.err_type == "not_found" or result.error.code == "NOT_FOUND"


def test_get_research_status_controller_rate_limit_exceeded():
    factory = MockInfrastructureFactory(allow_rate_limit=False)
    controller = GetResearchStatusController(factory=factory)

    dto = GetResearchStatusInputDTO(job_id="55555555-5555-5555-5555-555555555555")
    result = controller.run(dto, ctx=Metadata(user="10.0.0.1", ip="10.0.0.1"))

    assert result.is_err() is True
    assert result.error.err_type == "rate_limit" or result.error.code == "rate_limit"


def test_execute_research_worker_controller_success():
    factory = MockInfrastructureFactory()
    controller = ExecuteResearchWorkerController(factory=factory)

    dto = ExecuteResearchWorkerInputDTO(job_id="66666666-6666-6666-6666-666666666666", topic="Serverless Architecture")
    result = controller.run(dto)

    assert result.is_ok() is True
    assert result.value.status == "SUCCESS"
    assert result.value.s3_key == "reports/66666666-6666-6666-6666-666666666666.md"
    assert "66666666-6666-6666-6666-666666666666" in factory.storage.reports
