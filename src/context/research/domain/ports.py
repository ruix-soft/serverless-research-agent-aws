from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

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
    """Port for persisting and retrieving research reports."""
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


class IAsyncWorkerInvokerPort(ABC):
    """Port for invoking the background research worker."""
    @abstractmethod
    def invoke_worker(self, job_id: str, topic: str) -> None:
        """Triggers the async worker execution without waiting for completion."""
        pass


class IResearchAgentPort(ABC):
    """Port for AI Research execution."""
    @abstractmethod
    def execute_research(self, topic: str) -> str:
        """Executes the research agent workflow and returns markdown content."""
        pass


from context.kit.service.rate_limiter_service import RateLimiterService


class IInfrastructureFactory(ABC):
    """Abstract Factory to provide infrastructure adapters and cross-cutting ports."""
    @abstractmethod
    def create_report_storage(self) -> IReportStoragePort:
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


