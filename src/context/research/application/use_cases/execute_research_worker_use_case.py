from dataclasses import dataclass
from typing import Optional, Any
from context.kit.chain import ChainBuilder, BaseChainStep
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, new_domain_error
from context.kit.errors.validation_error import new_validation_error
from context.research.application.dtos.execute_research_worker_dto import (
    ExecuteResearchWorkerInputDTO,
    ExecuteResearchWorkerOutputDTO
)
from context.research.domain.ports import (
    IResearchAgentPort,
    IReportStoragePort
)


@dataclass
class ExecuteResearchWorkerContext:
    """Shared pipeline context for ExecuteResearchWorkerUseCase chain."""
    job_id: Optional[str] = None
    topic: Optional[str] = None
    report_content: Optional[str] = None
    s3_key: Optional[str] = None


class ValidateWorkerPayloadStep(BaseChainStep[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO, ExecuteResearchWorkerContext]):
    """Validates the worker input payload."""

    def name(self) -> str:
        return "ValidateWorkerPayloadStep"

    def execute(
        self,
        input_dto: ExecuteResearchWorkerInputDTO,
        shared_context: ExecuteResearchWorkerContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[ExecuteResearchWorkerOutputDTO], DomainError]:
        if not input_dto.job_id or not input_dto.job_id.strip():
            return Result.err(new_validation_error("El campo 'job_id' es obligatorio."))
        if not input_dto.topic or not input_dto.topic.strip():
            return Result.err(new_validation_error("El campo 'topic' es obligatorio."))

        shared_context.job_id = input_dto.job_id.strip()
        shared_context.topic = input_dto.topic.strip()
        return Result.ok(None)


class RunAgentReasoningStep(BaseChainStep[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO, ExecuteResearchWorkerContext]):
    """Executes AI research reasoning and tool searches via the agent port."""

    def __init__(self, research_agent: IResearchAgentPort):
        self._research_agent = research_agent

    def name(self) -> str:
        return "RunAgentReasoningStep"

    def execute(
        self,
        input_dto: ExecuteResearchWorkerInputDTO,
        shared_context: ExecuteResearchWorkerContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[ExecuteResearchWorkerOutputDTO], DomainError]:
        try:
            assert shared_context.topic is not None
            report_content = self._research_agent.execute_research(shared_context.topic)
            shared_context.report_content = report_content
            return Result.ok(None)
        except Exception as e:
            return Result.err(new_domain_error("infrastructure_error", f"Error ejecutando agente de investigación: {str(e)}"))


class PersistReportStorageStep(BaseChainStep[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO, ExecuteResearchWorkerContext]):
    """Uploads the generated report to S3 object storage."""

    def __init__(self, report_storage: IReportStoragePort):
        self._report_storage = report_storage

    def name(self) -> str:
        return "PersistReportStorageStep"

    def execute(
        self,
        input_dto: ExecuteResearchWorkerInputDTO,
        shared_context: ExecuteResearchWorkerContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[ExecuteResearchWorkerOutputDTO], DomainError]:
        try:
            assert shared_context.job_id is not None
            assert shared_context.report_content is not None
            s3_key = self._report_storage.upload_report(
                job_id=shared_context.job_id,
                content=shared_context.report_content,
                extension="md"
            )
            shared_context.s3_key = s3_key
            return Result.ok(None)
        except Exception as e:
            return Result.err(new_domain_error("infrastructure_error", f"Error persistiendo reporte en S3: {str(e)}"))


class BuildWorkerOutputStep(BaseChainStep[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO, ExecuteResearchWorkerContext]):
    """Constructs the ExecuteResearchWorkerOutputDTO response."""

    def name(self) -> str:
        return "BuildWorkerOutputStep"

    def execute(
        self,
        input_dto: ExecuteResearchWorkerInputDTO,
        shared_context: ExecuteResearchWorkerContext,
        ctx: Optional[Any] = None
    ) -> Result[ExecuteResearchWorkerOutputDTO, DomainError]:
        output = ExecuteResearchWorkerOutputDTO(
            job_id=shared_context.job_id,
            status="SUCCESS",
            s3_key=shared_context.s3_key
        )
        return Result.ok(output)


class ExecuteResearchWorkerUseCase:
    """
    Use case to run the research agent and store results in S3.
    Orchestrated strictly via Chain of Responsibility.
    """

    def __init__(self, research_agent: IResearchAgentPort, report_storage: IReportStoragePort):
        self._research_agent = research_agent
        self._report_storage = report_storage
        self._pipeline = (
            ChainBuilder[ExecuteResearchWorkerInputDTO, ExecuteResearchWorkerOutputDTO, ExecuteResearchWorkerContext]()
            .add_handler(ValidateWorkerPayloadStep())
            .add_handler(RunAgentReasoningStep(research_agent=self._research_agent))
            .add_handler(PersistReportStorageStep(report_storage=self._report_storage))
            .add_handler(BuildWorkerOutputStep())
            .build()
        )

    def execute(self, input_dto: ExecuteResearchWorkerInputDTO, ctx: Optional[Any] = None) -> Result[ExecuteResearchWorkerOutputDTO, DomainError]:
        shared_context = ExecuteResearchWorkerContext()
        return self._pipeline.handle(input_dto, shared_context, ctx)
