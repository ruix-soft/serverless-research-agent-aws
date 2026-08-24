from typing import Optional, Any
from app.controllers.base import ICommandHandler, BaseController
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.research.application.dtos.start_research_dto import (
    StartResearchInputDTO,
    StartResearchOutputDTO
)
from context.research.application.use_cases.start_research_use_case import StartResearchUseCase
from context.research.domain.ports import IInfrastructureFactory
from context.research.infrastructure.infrastructure_factory import InfrastructureFactory


class StartResearchCommandHandler(ICommandHandler[StartResearchInputDTO, StartResearchOutputDTO]):
    """Command Handler wrapper delegating to StartResearchUseCase."""

    def __init__(self, use_case: StartResearchUseCase):
        super().__init__(command_type="StartResearchCommand")
        self._use_case = use_case

    def handle(self, input_dto: StartResearchInputDTO, ctx: Optional[Any] = None) -> Result[StartResearchOutputDTO, DomainError]:
        return self._use_case.execute(input_dto, ctx)


class StartResearchController(BaseController[StartResearchInputDTO, StartResearchOutputDTO]):
    """
    Controller for initiating research tasks.
    Follows arch-core strict sequential construction:
    1. Instantiate Use Case using InfrastructureFactory.
    2. Wrap Use Case in CommandHandler.
    3. Retrieve generic observability tools.
    4. Stack behavior decorators (LoggingDecorator, MetricsDecorator).
    5. Expose run(dto) -> Result.
    """

    def __init__(self, factory: Optional[IInfrastructureFactory] = None):
        factory = factory or InfrastructureFactory()

        # 1. Instantiate Use Case
        use_case = StartResearchUseCase(worker_invoker=factory.create_async_worker_invoker())

        # 2. Wrap in CommandHandler
        command_handler = StartResearchCommandHandler(use_case)

        # 3. Retrieve observability tools
        logger = factory.create_logger()
        metrics = factory.create_metrics()

        # 4. Stack decorators
        logging_decorated = LoggingDecorator(command_handler, logger=logger, handler_name="StartResearchCommandHandler")
        metrics_decorated = MetricsDecorator(logging_decorated, metrics=metrics, metric_namespace="StartResearch")

        # 5. Initialize base controller
        super().__init__(metrics_decorated)
