from typing import Optional, Any
from app.controllers.base import ICommandHandler, BaseController
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.research.application.dtos.execute_research_worker_dto import (
    ExecuteResearchWorkerInputDTO,
    ExecuteResearchWorkerOutputDTO
)
from context.research.application.use_cases.execute_research_worker_use_case import ExecuteResearchWorkerUseCase
from context.research.domain.ports import IInfrastructureFactory
from context.research.infrastructure.infrastructure_factory import InfrastructureFactory


class ExecuteResearchWorkerCommandHandler(ICommandHandler[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO]):
    """Command Handler wrapper delegating to ExecuteResearchWorkerUseCase."""

    def __init__(self, use_case: ExecuteResearchWorkerUseCase):
        super().__init__(command_type="ExecuteResearchWorkerCommand")
        self._use_case = use_case

    def handle(self, input_dto: ExecuteResearchWorkerInputDTO, ctx: Optional[Any] = None) -> Result[ExecuteResearchWorkerOutputDTO, DomainError]:
        return self._use_case.execute(input_dto, ctx)


class ExecuteResearchWorkerController(BaseController[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO]):
    """
    Controller for background worker research execution.
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
        use_case = ExecuteResearchWorkerUseCase(
            research_agent=factory.create_research_agent(),
            report_storage=factory.create_report_storage()
        )

        # 2. Wrap in CommandHandler
        command_handler = ExecuteResearchWorkerCommandHandler(use_case)

        # 3. Retrieve observability tools
        logger = factory.create_logger()
        metrics = factory.create_metrics()

        # 4. Stack decorators
        logging_decorated = LoggingDecorator(command_handler, logger=logger, handler_name="ExecuteResearchWorkerCommandHandler")
        metrics_decorated = MetricsDecorator(logging_decorated, metrics=metrics, metric_namespace="ExecuteResearchWorker")

        # 5. Initialize base controller
        super().__init__(metrics_decorated)
