from dataclasses import dataclass
from typing import Optional, Any, List
from context.kit.chain import ChainBuilder, BaseChainStep
from context.kit.chain.chain_step_logging_decorator import new_step_logging_decorator
from context.kit.service.logger_service import LoggerService
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, new_domain_error
from context.kit.errors.validation_error import new_validation_error
from context.kit.errors.not_found_error import new_not_found_error
from context.research.application.dtos.get_research_status_dto import (
    GetResearchStatusInputDTO,
    GetResearchStatusOutputDTO
)
from context.research.domain.entities.research_job import ResearchJob
from context.research.domain.ports import IReportStoragePort, IResearchJobRepository


@dataclass
class GetResearchStatusContext:
    """Shared pipeline context for GetResearchStatusUseCase chain."""
    job_id: Optional[str] = None
    job: Optional[ResearchJob] = None
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


class FindResearchJobStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Queries the Job Repository in DynamoDB to retrieve the ResearchJob aggregate root."""

    def __init__(self, job_repository: Optional[IResearchJobRepository] = None, report_storage: Optional[IReportStoragePort] = None):
        self._job_repository = job_repository
        self._report_storage = report_storage

    def name(self) -> str:
        return "FindResearchJobStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[GetResearchStatusOutputDTO], DomainError]:
        job_id = shared_context.job_id
        assert job_id is not None

        if self._job_repository is not None:
            try:
                job_opt = self._job_repository.find_by_id(job_id)
                if job_opt.is_empty():
                    # Fallback check on S3 if storage is available before raising 404
                    if self._report_storage and self._report_storage.report_exists(job_id):
                        job = ResearchJob.create(topic="Research Task", id=job_id)
                        job.mark_as_completed(f"reports/{job_id}.md")
                        shared_context.job = job
                        return Result.ok(None)
                    return Result.err(new_not_found_error(f"Investigación con ID '{job_id}' no encontrada."))
                shared_context.job = job_opt.get()
                return Result.ok(None)
            except Exception as e:
                return Result.err(new_domain_error("infrastructure_error", f"Error consultando repositorio de trabajos: {str(e)}"))

        # Fallback to S3 storage existence if repository is not injected
        if self._report_storage is not None:
            exists = self._report_storage.report_exists(job_id)
            job = ResearchJob.create(topic="Research Task", id=job_id)
            if exists:
                job.mark_as_completed(f"reports/{job_id}.md")
            shared_context.job = job
            return Result.ok(None)

        return Result.err(new_domain_error("configuration_error", "No repository or storage port configured"))


class ResolvePresignedUrlStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Generates presigned S3 download URL if the job is completed."""

    def __init__(self, report_storage: IReportStoragePort):
        self._report_storage = report_storage

    def name(self) -> str:
        return "ResolvePresignedUrlStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[Optional[GetResearchStatusOutputDTO], DomainError]:
        job = shared_context.job
        assert job is not None

        if job.is_completed() and self._report_storage:
            job_id_str = job.id.value() if callable(getattr(job.id, "value", None)) else str(job.id)
            s3_key = job.s3_key or f"reports/{job_id_str}.md"
            try:
                presigned_url = self._report_storage.generate_presigned_url(s3_key, expiration_seconds=3600)
                shared_context.presigned_url = presigned_url
            except Exception as e:
                return Result.err(new_domain_error("infrastructure_error", f"Error generando URL de descarga: {str(e)}"))

        return Result.ok(None)


class BuildGetStatusOutputStep(BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]):
    """Constructs the GetResearchStatusOutputDTO response from the domain entity."""

    def name(self) -> str:
        return "BuildGetStatusOutputStep"

    def execute(
        self,
        input_dto: GetResearchStatusInputDTO,
        shared_context: GetResearchStatusContext,
        ctx: Optional[Any] = None
    ) -> Result[GetResearchStatusOutputDTO, DomainError]:
        job = shared_context.job
        assert job is not None

        job_id_str = job.id.value() if callable(getattr(job.id, "value", None)) else str(job.id)
        topic_str = job.topic.value() if callable(getattr(job.topic, "value", None)) else str(job.topic)

        if job.is_completed():
            output = GetResearchStatusOutputDTO(
                job_id=job_id_str,
                topic=topic_str,
                status="COMPLETED",
                s3_report_url=shared_context.presigned_url,
                message="Investigación completada exitosamente."
            )
        elif job.is_failed():
            output = GetResearchStatusOutputDTO(
                job_id=job_id_str,
                topic=topic_str,
                status="FAILED",
                error=job.error_message or "La investigación falló durante la ejecución.",
                message="Ocurrió un error al procesar la investigación."
            )
        else:
            output = GetResearchStatusOutputDTO(
                job_id=job_id_str,
                topic=topic_str,
                status="IN_PROGRESS",
                message="La investigación se encuentra en progreso."
            )

        return Result.ok(output)


class GetResearchStatusUseCase:
    """
    Use case to query research status and retrieve presigned report URLs.
    Orchestrated strictly via Chain of Responsibility.
    """

    def __init__(
        self,
        report_storage: IReportStoragePort,
        job_repository: Optional[IResearchJobRepository] = None,
        logger: Optional[LoggerService] = None,
    ):
        self._report_storage = report_storage
        self._job_repository = job_repository
        self._logger = logger

        builder = ChainBuilder[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]()
        steps: List[BaseChainStep[GetResearchStatusInputDTO, GetResearchStatusOutputDTO, GetResearchStatusContext]] = [
            ValidateGetStatusStep(),
            FindResearchJobStep(job_repository=self._job_repository, report_storage=self._report_storage),
            ResolvePresignedUrlStep(report_storage=self._report_storage),
            BuildGetStatusOutputStep(),
        ]

        for step in steps:
            handler = new_step_logging_decorator(step, self._logger) if self._logger else step
            builder.add_handler(handler)

        self._pipeline = builder.build()

    def execute(self, input_dto: GetResearchStatusInputDTO, ctx: Optional[Any] = None) -> Result[GetResearchStatusOutputDTO, DomainError]:
        shared_context = GetResearchStatusContext()
        return self._pipeline.handle(input_dto, shared_context, ctx)
