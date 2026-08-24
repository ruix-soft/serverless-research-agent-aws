from dataclasses import dataclass
from typing import Optional, Any, Union, List
from context.kit.chain import ChainBuilder, BaseChainStep
from context.kit.chain.chain_step_logging_decorator import new_step_logging_decorator
from context.kit.chain.chain_step_tracing_decorator import new_step_tracing_decorator
from context.kit.service.logger_service import LoggerService
from context.kit.service.tracer_service import TracerService
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, new_domain_error
from context.kit.errors.validation_error import new_validation_error
from context.kit.vo.uuid import random_uuid
from context.research.application.dtos.start_research_dto import (
    StartResearchInputDTO,
    StartResearchOutputDTO
)
from context.research.domain.ports import IStateMachineInvokerPort, IAsyncWorkerInvokerPort


@dataclass
class StartResearchContext:
    """Shared pipeline context for StartResearchUseCase chain."""
    job_id: Optional[str] = None
    status_url: Optional[str] = None


class ValidateStartResearchStep(BaseChainStep[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]):
    """Validates topic and initializes the job ID."""

    def name(self) -> str:
        return "ValidateStartResearchStep"

    def execute(
        self,
        input_dto: StartResearchInputDTO,
        shared_context: StartResearchContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[StartResearchOutputDTO], DomainError]:
        if not input_dto.topic or not input_dto.topic.strip():
            return Result.err(new_validation_error("El campo 'topic' es obligatorio y no puede estar vacío."))

        job_id = random_uuid().value()
        shared_context.job_id = job_id
        shared_context.status_url = f"/research/{job_id}"
        return Result.ok(None)


class InvokeStateMachineStep(BaseChainStep[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]):
    """Invokes the AWS Step Functions state machine with the initialized job ID."""

    def __init__(self, invoker: Union[IStateMachineInvokerPort, IAsyncWorkerInvokerPort]):
        self._invoker = invoker

    def name(self) -> str:
        return "InvokeStateMachineStep"

    def execute(
        self,
        input_dto: StartResearchInputDTO,
        shared_context: StartResearchContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[StartResearchOutputDTO], DomainError]:
        try:
            assert shared_context.job_id is not None
            topic = input_dto.topic.strip()
            if hasattr(self._invoker, "start_execution"):
                self._invoker.start_execution(
                    job_id=shared_context.job_id,
                    topic=topic
                )
            elif hasattr(self._invoker, "invoke_worker"):
                self._invoker.invoke_worker(
                    job_id=shared_context.job_id,
                    topic=topic
                )
            return Result.ok(None)
        except Exception as e:
            return Result.err(new_domain_error("infrastructure_error", f"Error iniciando orquestación: {str(e)}"))


class BuildStartResearchOutputStep(BaseChainStep[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]):
    """Constructs the final StartResearchOutputDTO response."""

    def name(self) -> str:
        return "BuildStartResearchOutputStep"

    def execute(
        self,
        input_dto: StartResearchInputDTO,
        shared_context: StartResearchContext,
        ctx: Optional[Any] = None
    ) -> Result[StartResearchOutputDTO, DomainError]:
        output = StartResearchOutputDTO(
            job_id=shared_context.job_id,
            status="IN_PROGRESS",
            message="Investigación iniciada. Consulta el estado en el endpoint proporcionado.",
            status_url=shared_context.status_url
        )
        return Result.ok(output)


class StartResearchUseCase:
    """
    Use case to initiate asynchronous research processing.
    Orchestrated strictly via Chain of Responsibility.
    """

    def __init__(
        self,
        state_machine_invoker: Union[IStateMachineInvokerPort, IAsyncWorkerInvokerPort],
        logger: Optional[LoggerService] = None,
        tracer: Optional[TracerService] = None,
    ):
        self._state_machine_invoker = state_machine_invoker
        self._logger = logger
        self._tracer = tracer

        builder = ChainBuilder[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]()
        steps: List[BaseChainStep[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]] = [
            ValidateStartResearchStep(),
            InvokeStateMachineStep(invoker=self._state_machine_invoker),
            BuildStartResearchOutputStep(),
        ]

        for step in steps:
            handler: Any = step
            if self._tracer:
                handler = new_step_tracing_decorator(handler, self._tracer)
            if self._logger:
                handler = new_step_logging_decorator(handler, self._logger)
            builder.add_handler(handler)

        self._pipeline = builder.build()

    def execute(self, input_dto: StartResearchInputDTO, ctx: Optional[Any] = None) -> Result[StartResearchOutputDTO, DomainError]:
        shared_context = StartResearchContext()
        return self._pipeline.handle(input_dto, shared_context, ctx)
