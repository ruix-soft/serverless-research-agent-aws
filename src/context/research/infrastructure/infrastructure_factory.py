from typing import Optional
from context.kit.service.rate_limiter_service import RateLimiterService
from context.research.domain.ports import (
    IInfrastructureFactory,
    IReportStoragePort,
    IAsyncWorkerInvokerPort,
    IResearchAgentPort,
    ILoggerPort,
    IMetricsPort
)
from context.research.infrastructure.s3_storage_adapter import S3StorageAdapter
from context.research.infrastructure.lambda_invoker_adapter import LambdaInvokerAdapter
from context.research.infrastructure.bedrock_agent_adapter import BedrockAgentAdapter
from context.research.infrastructure.powertools_adapters import (
    PowertoolsLoggerAdapter,
    PowertoolsMetricsAdapter
)
from context.research.infrastructure.dynamodb_rate_limiter_adapter import DynamoDBRateLimiterAdapter

# Global / module scope resource instances
_default_s3_storage = None
_default_lambda_invoker = None
_default_research_agent = None
_default_logger = None
_default_metrics = None
_default_rate_limiter = None


class InfrastructureFactory(IInfrastructureFactory):
    """Concrete Infrastructure Factory providing ports to controllers and application layers."""

    def __init__(
        self,
        report_storage: Optional[IReportStoragePort] = None,
        async_worker_invoker: Optional[IAsyncWorkerInvokerPort] = None,
        research_agent: Optional[IResearchAgentPort] = None,
        logger: Optional[ILoggerPort] = None,
        metrics: Optional[IMetricsPort] = None,
        rate_limiter: Optional[RateLimiterService] = None,
    ):
        global _default_s3_storage, _default_lambda_invoker, _default_research_agent, _default_logger, _default_metrics, _default_rate_limiter

        if _default_s3_storage is None:
            _default_s3_storage = S3StorageAdapter()
        if _default_lambda_invoker is None:
            _default_lambda_invoker = LambdaInvokerAdapter()
        if _default_research_agent is None:
            _default_research_agent = BedrockAgentAdapter()
        if _default_logger is None:
            _default_logger = PowertoolsLoggerAdapter()
        if _default_metrics is None:
            _default_metrics = PowertoolsMetricsAdapter()
        if _default_rate_limiter is None:
            _default_rate_limiter = DynamoDBRateLimiterAdapter()

        self._report_storage = report_storage or _default_s3_storage
        self._async_worker_invoker = async_worker_invoker or _default_lambda_invoker
        self._research_agent = research_agent or _default_research_agent
        self._logger = logger or _default_logger
        self._metrics = metrics or _default_metrics
        self._rate_limiter = rate_limiter or _default_rate_limiter

    def create_report_storage(self) -> IReportStoragePort:
        return self._report_storage

    def create_async_worker_invoker(self) -> IAsyncWorkerInvokerPort:
        return self._async_worker_invoker

    def create_research_agent(self) -> IResearchAgentPort:
        return self._research_agent

    def create_logger(self) -> ILoggerPort:
        return self._logger

    def create_metrics(self) -> IMetricsPort:
        return self._metrics

    def create_rate_limiter(self) -> RateLimiterService:
        return self._rate_limiter
