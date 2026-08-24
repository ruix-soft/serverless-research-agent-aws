from dataclasses import dataclass
from typing import Optional, Any
from context.kit.chain import ChainBuilder, BaseChainStep
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, new_domain_error
from context.kit.errors.validation_error import new_validation_error
from context.kit.vo.uuid import random_uuid
from context.research.application.dtos.start_research_dto import (
    StartResearchInputDTO,
    StartResearchOutputDTO
)
from context.research.domain.ports import IAsyncWorkerInvokerPort


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


class InvokeWorkerStep(BaseChainStep[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]):
    """Invokes the background async worker with the initialized job ID."""

    def __init__(self, worker_invoker: IAsyncWorkerInvokerPort):
        self._worker_invoker = worker_invoker

    def name(self) -> str:
        return "InvokeWorkerStep"

    def execute(
        self,
        input_dto: StartResearchInputDTO,
        shared_context: StartResearchContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[StartResearchOutputDTO], DomainError]:
        try:
            assert shared_context.job_id is not None
            self._worker_invoker.invoke_worker(
                job_id=shared_context.job_id,
                topic=input_dto.topic.strip()
            )
            return Result.ok(None)
        except Exception as e:
            return Result.err(new_domain_error("infrastructure_error", f"Error invocando worker asíncrono: {str(e)}"))


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

    def __init__(self, worker_invoker: IAsyncWorkerInvokerPort):
        self._worker_invoker = worker_invoker
        self._pipeline = (
            ChainBuilder[StartResearchInputDTO, StartResearchOutputDTO, StartResearchContext]()
            .add_handler(ValidateStartResearchStep())
            .add_handler(InvokeWorkerStep(worker_invoker=self._worker_invoker))
            .add_handler(BuildStartResearchOutputStep())
            .build()
        )

    def execute(self, input_dto: StartResearchInputDTO, ctx: Optional[Any] = None) -> Result[StartResearchOutputDTO, DomainError]:
        shared_context = StartResearchContext()
        return self._pipeline.handle(input_dto, shared_context, ctx)
