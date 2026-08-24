from typing import Optional, Any
from app.controllers.base import IQueryHandler, BaseController
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.kit.query.query_rate_limit_decorator import (
    QueryRateLimitDecorator,
    QueryRateLimitOptions,
)
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.research.application.dtos.get_research_status_dto import (
    GetResearchStatusInputDTO,
    GetResearchStatusOutputDTO,
)
from context.research.application.use_cases.get_research_status_use_case import GetResearchStatusUseCase
from context.research.domain.ports import IInfrastructureFactory
from context.research.infrastructure.infrastructure_factory import InfrastructureFactory


class GetResearchStatusQueryHandler(IQueryHandler[GetResearchStatusInputDTO, GetResearchStatusOutputDTO]):
    """Query Handler wrapper delegating to GetResearchStatusUseCase."""

    def __init__(self, use_case: GetResearchStatusUseCase):
        super().__init__(query_type="GetResearchStatusQuery")
        self._use_case = use_case

    def handle(self, input_dto: GetResearchStatusInputDTO, ctx: Optional[Any] = None) -> Result[GetResearchStatusOutputDTO, DomainError]:
        return self._use_case.execute(input_dto, ctx)


class GetResearchStatusController(BaseController[GetResearchStatusInputDTO, GetResearchStatusOutputDTO]):
    """
    Controller for checking research status and retrieving presigned URLs.
    Follows arch-core strict sequential construction:
    1. Instantiate Use Case using InfrastructureFactory.
    2. Wrap Use Case in QueryHandler.
    3. Apply Rate Limiter Decorator (DynamoDB backed).
    4. Retrieve generic observability tools.
    5. Stack behavior decorators (LoggingDecorator, MetricsDecorator).
    6. Expose run(dto, ctx) -> Result.
    """

    def __init__(
        self,
        factory: Optional[IInfrastructureFactory] = None,
        rate_limit: int = 30,
        rate_window_ms: int = 60000,
    ):
        factory = factory or InfrastructureFactory()

        # 1. Instantiate Use Case
        use_case = GetResearchStatusUseCase(report_storage=factory.create_report_storage())

        # 2. Wrap in QueryHandler
        query_handler = GetResearchStatusQueryHandler(use_case)

        # 3. Apply Rate Limiter Decorator
        limiter = factory.create_rate_limiter()
        rate_limit_options = QueryRateLimitOptions[GetResearchStatusInputDTO](
            limit=rate_limit,
            window_ms=rate_window_ms,
            key_resolver=lambda payload, q_type, meta: (
                f"get_status:{payload.job_id}:{meta.ip if meta and meta.ip else (meta.user if meta and meta.user else 'global')}"
            ),
        )
        rate_limited_handler = QueryRateLimitDecorator(
            base=query_handler,
            limiter=limiter,
            options=rate_limit_options,
        )

        # 4. Retrieve observability tools
        logger = factory.create_logger()
        metrics = factory.create_metrics()

        # 5. Stack decorators
        logging_decorated = LoggingDecorator(rate_limited_handler, logger=logger, handler_name="GetResearchStatusQueryHandler")
        metrics_decorated = MetricsDecorator(logging_decorated, metrics=metrics, metric_namespace="GetResearchStatus")

        # 6. Initialize base controller
        super().__init__(metrics_decorated)
