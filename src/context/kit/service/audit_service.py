from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from context.kit.dtos.metadata import Metadata


@dataclass
class SerializedError:
    """
    Representa un error estructurado para logs y auditoría.
    """

    name: str
    message: str
    stack: Optional[str] = None
    code: Optional[str] = None
    cause: Optional["SerializedError"] = None


@dataclass
class AuditRecord:
    """
    AuditRecord representa una entrada de auditoría completa.
    """

    type: str
    timestamp: datetime
    metadata: Optional[Metadata] = None
    payload: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Any] = None


class AuditService(ABC):
    """
    AuditService define el contrato para registrar eventos de auditoría.
    """

    @abstractmethod
    def record(self, entry: AuditRecord, ctx: Optional[Any] = None) -> None:
        """Guarda una entrada de auditoría."""
        pass

    def Record(self, ctx: Optional[Any], entry: AuditRecord) -> None:
        """Alias para compatibilidad con Go (Record)."""
        self.record(entry, ctx)


def new_serialized_error(err: Any) -> Optional[SerializedError]:
    """Helper NewSerializedError."""
    if err is None:
        return None
    return SerializedError(
        name=err.__class__.__name__ if hasattr(err, "__class__") else "Error",
        message=str(err),
    )


def NewSerializedError(err: Any) -> Optional[SerializedError]:
    return new_serialized_error(err)

