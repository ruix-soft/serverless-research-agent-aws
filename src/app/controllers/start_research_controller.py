from typing import Optional, Any
from app.controllers.base import ICommandHandler, BaseController
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.kit.command.command_rate_limit_decorator import (
    CommandRateLimitDecorator,
    RateLimitOptions,
)
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.research.application.dtos.start_research_dto import (
    StartResearchInputDTO,
    StartResearchOutputDTO,
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
    Follows Luis Ruiz architectural methodology (arch-core) strict sequential construction:
    1. Instantiate Use Case using InfrastructureFactory (Step Functions State Machine).
    2. Wrap Use Case in CommandHandler.
    3. Apply Rate Limiter Decorator (DynamoDB backed).
    4. Retrieve generic observability tools.
    5. Stack behavior decorators (LoggingDecorator, MetricsDecorator).
    6. Expose run(dto, ctx) -> Result.
    """

    def __init__(
        self,
        factory: Optional[IInfrastructureFactory] = None,
        rate_limit: int = 5,
        rate_window_ms: int = 60000,
    ):
        factory = factory or InfrastructureFactory()

        # 1. Retrieve observability tools
        logger = factory.create_logger()
        tracer = factory.create_tracer()
        metrics = factory.create_metrics()

        # 2. Instantiate Use Case with State Machine Invoker and injected logger & tracer
        state_machine_invoker = factory.create_state_machine_invoker()
        use_case = StartResearchUseCase(
            state_machine_invoker=state_machine_invoker,
            logger=logger,
            tracer=tracer,
        )

        # 3. Wrap in CommandHandler
        command_handler = StartResearchCommandHandler(use_case)

        # 4. Apply Rate Limiter Decorator
        limiter = factory.create_rate_limiter()
        rate_limit_options = RateLimitOptions[StartResearchInputDTO](
            limit=rate_limit,
            window_ms=rate_window_ms,
            key_resolver=lambda payload, cmd_type, meta: (
                f"start_research:{meta.ip if meta and meta.ip else (meta.user if meta and meta.user else 'global')}"
            ),
        )
        rate_limited_handler = CommandRateLimitDecorator(
            base=command_handler,
            limiter=limiter,
            options=rate_limit_options,
        )

        # 5. Stack decorators
        logging_decorated = LoggingDecorator(rate_limited_handler, logger=logger, handler_name="StartResearchCommandHandler")
        metrics_decorated = MetricsDecorator(logging_decorated, metrics=metrics, metric_namespace="StartResearch")

        # 6. Initialize base controller
        super().__init__(metrics_decorated)
