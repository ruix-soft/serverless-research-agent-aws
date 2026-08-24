from dataclasses import dataclass
from typing import Optional, Any
from context.kit.chain import ChainBuilder, BaseChainStep
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, new_domain_error
from context.kit.errors.validation_error import new_validation_error
from context.research.application.dtos.get_research_status_dto import (
    GetResearchStatusInputDTO,
    GetResearchStatusOutputDTO
)
from context.research.domain.ports import IReportStoragePort


@dataclass
class GetResearchStatusContext:
    """Shared pipeline context for GetResearchStatusUseCase chain."""
    job_id: Optional[str] = None
    exists: bool = False
    presigned_url: Optional[str] = None


class ValidateGetStatusStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Validates the job ID."""

    def name(self) -> str:
        return "ValidateGetStatusStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[GetResearchStatusOutputDTO], DomainError]:
        if not input_dto.job_id or not input_dto.job_id.strip():
            return Result.err(new_validation_error("El campo 'job_id' es obligatorio."))

        shared_context.job_id = input_dto.job_id.strip()
        return Result.ok(None)


class CheckReportStorageStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Checks S3 report storage and generates presigned URL if report is ready."""

    def __init__(self, report_storage: IReportStoragePort):
        self._report_storage = report_storage

    def name(self) -> str:
        return "CheckReportStorageStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[GetResearchStatusOutputDTO], DomainError]:
        try:
            assert shared_context.job_id is not None
            exists = self._report_storage.report_exists(shared_context.job_id)
            shared_context.exists = exists
            if exists:
                object_key = f"reports/{shared_context.job_id}.md"
                presigned_url = self._report_storage.generate_presigned_url(object_key, expiration_seconds=3600)
                shared_context.presigned_url = presigned_url
            return Result.ok(None)
        except Exception as e:
            return Result.err(new_domain_error("infrastructure_error", f"Error consultando almacenamiento de reportes: {str(e)}"))


class BuildGetStatusOutputStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Constructs the GetResearchStatusOutputDTO response."""

    def name(self) -> str:
        return "BuildGetStatusOutputStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[GetResearchStatusOutputDTO, DomainError]:
        if shared_context.exists:
            output = GetResearchStatusOutputDTO(
                job_id=shared_context.job_id,
                status="COMPLETED",
                s3_report_url=shared_context.presigned_url
            )
        else:
            output = GetResearchStatusOutputDTO(
                job_id=shared_context.job_id,
                status="IN_PROGRESS",
                message="El reporte aún se está generando."
            )
        return Result.ok(output)


class GetResearchStatusUseCase:
    """
    Use case to query research status and retrieve presigned report URLs.
    Orchestrated strictly via Chain of Responsibility.
    """

    def __init__(self, report_storage: IReportStoragePort):
        self._report_storage = report_storage
        self._pipeline = (
            ChainBuilder[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]()
            .add_handler(ValidateGetStatusStep())
            .add_handler(CheckReportStorageStep(report_storage=self._report_storage))
            .add_handler(BuildGetStatusOutputStep())
            .build()
        )

    def execute(self, input_dto: GetResearchStatusInputDTO, ctx: Optional[Any] = None) -> Result[GetResearchStatusOutputDTO, DomainError]:
        shared_context = GetResearchStatusContext()
        return self._pipeline.handle(input_dto, shared_context, ctx)
