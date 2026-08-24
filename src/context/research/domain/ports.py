from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from context.kit.dtos.optional import Optional as KitOptional
from context.kit.service.rate_limiter_service import RateLimiterService
from context.research.domain.entities.research_job import ResearchJob


class ILoggerPort(ABC):
    """Port for structured logging."""
    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        pass


class IMetricsPort(ABC):
    """Port for application metrics."""
    @abstractmethod
    def add_metric(self, name: str, unit: str, value: float) -> None:
        pass


class IReportStoragePort(ABC):
    """Port for persisting and retrieving research reports in S3."""
    @abstractmethod
    def upload_report(self, job_id: str, content: str, extension: str = "md") -> str:
        """Uploads report content and returns the stored object key/path."""
        pass

    @abstractmethod
    def generate_presigned_url(self, object_key: str, expiration_seconds: int = 3600) -> str:
        """Generates a secure presigned URL for downloading the report."""
        pass

    @abstractmethod
    def report_exists(self, job_id: str, extension: str = "md") -> bool:
        """Checks if a report exists for the given job_id."""
        pass


class IResearchJobRepository(ABC):
    """Port for persisting and querying ResearchJob aggregate roots in DynamoDB."""
    @abstractmethod
    def save(self, job: ResearchJob) -> None:
        """Saves or updates a ResearchJob entity."""
        pass

    @abstractmethod
    def find_by_id(self, job_id: str) -> KitOptional[ResearchJob]:
        """Finds a ResearchJob by its unique identifier."""
        pass


class IStateMachineInvokerPort(ABC):
    """Port for starting the AWS Step Functions research state machine."""
    @abstractmethod
    def start_execution(self, job_id: str, topic: str) -> None:
        """Triggers Step Functions state machine execution asynchronously."""
        pass


class IAsyncWorkerInvokerPort(ABC):
    """Port for invoking the background research worker directly (fallback / testing)."""
    @abstractmethod
    def invoke_worker(self, job_id: str, topic: str) -> None:
        pass


class IResearchAgentPort(ABC):
    """Port for AI Research execution (Bedrock + Tavily)."""
    @abstractmethod
    def execute_research(self, topic: str) -> str:
        pass


class IInfrastructureFactory(ABC):
    """Abstract Factory to provide infrastructure adapters and cross-cutting ports."""
    @abstractmethod
    def create_report_storage(self) -> IReportStoragePort:
        pass

    @abstractmethod
    def create_job_repository(self) -> IResearchJobRepository:
        pass

    @abstractmethod
    def create_state_machine_invoker(self) -> IStateMachineInvokerPort:
        pass

    @abstractmethod
    def create_async_worker_invoker(self) -> IAsyncWorkerInvokerPort:
        pass

    @abstractmethod
    def create_research_agent(self) -> IResearchAgentPort:
        pass

    @abstractmethod
    def create_logger(self) -> ILoggerPort:
        pass

    @abstractmethod
    def create_metrics(self) -> IMetricsPort:
        pass

    @abstractmethod
    def create_rate_limiter(self) -> RateLimiterService:
        pass
