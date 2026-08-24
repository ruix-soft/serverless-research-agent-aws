from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional, Any
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.serialize_error import serialize_error
from context.kit.service.audit_service import AuditService, AuditRecord

I = TypeVar("I")
O = TypeVar("O")


class CommandAuditDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandAuditDecorator envuelve un Command para registrar auditoría de cada ejecución.
    """

    def __init__(self, base: Handler[I, O], audit: AuditService) -> None:
        self._base = base
        self._audit = audit

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandAuditDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        cmd_type = self.command_type()
        meta = self.metadata()

        try:
            result = self._base.execute(payload, ctx)

            record = AuditRecord(
                type=cmd_type,
                timestamp=datetime.now(timezone.utc),
                metadata=meta,
                payload=payload,
                result=result.get() if result.is_ok() else None,
                error=serialize_error(result.get_error()) if result.is_error() else None,
            )

            try:
                self._audit.record(record, ctx)
            except Exception:
                pass

            return result
        except Exception as exc:
            record = AuditRecord(
                type=cmd_type,
                timestamp=datetime.now(timezone.utc),
                metadata=meta,
                payload=payload,
                result=None,
                error=serialize_error(exc),
            )
            try:
                self._audit.record(record, ctx)
            except Exception:
                pass
            raise


def new_command_audit_decorator(base: Handler[I, O], audit: AuditService) -> CommandAuditDecorator[I, O]:
    return CommandAuditDecorator(base, audit)


def NewCommandAuditDecorator(base: Handler[I, O], audit: AuditService) -> CommandAuditDecorator[I, O]:
    return new_command_audit_decorator(base, audit)

