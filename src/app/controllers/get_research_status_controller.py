from typing import Optional, Any
from app.controllers.base import IQueryHandler, BaseController
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.research.application.dtos.get_research_status_dto import (
    GetResearchStatusInputDTO,
    GetResearchStatusOutputDTO
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
    3. Retrieve generic observability tools.
    4. Stack behavior decorators (LoggingDecorator, MetricsDecorator).
    5. Expose run(dto) -> Result.
    """

    def __init__(self, factory: Optional[IInfrastructureFactory] = None):
        factory = factory or InfrastructureFactory()

        # 1. Instantiate Use Case
        use_case = GetResearchStatusUseCase(report_storage=factory.create_report_storage())

        # 2. Wrap in QueryHandler
        query_handler = GetResearchStatusQueryHandler(use_case)

        # 3. Retrieve observability tools
        logger = factory.create_logger()
        metrics = factory.create_metrics()

        # 4. Stack decorators
        logging_decorated = LoggingDecorator(query_handler, logger=logger, handler_name="GetResearchStatusQueryHandler")
        metrics_decorated = MetricsDecorator(logging_decorated, metrics=metrics, metric_namespace="GetResearchStatus")

        # 5. Initialize base controller
        super().__init__(metrics_decorated)
