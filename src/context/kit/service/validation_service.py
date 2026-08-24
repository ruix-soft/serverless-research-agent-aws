from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any
from context.kit.dtos.metadata import Metadata


@dataclass
class ValidationResult:
    """
    ValidationResult representa el resultado de una validación.
    """

    valid: bool
    message: Optional[str] = None
    details: Optional[Any] = None


class ValidationService(ABC):
    """
    ValidationService define el contrato para validar estructuras de datos.
    """

    @abstractmethod
    def validate(
        self,
        payload: Any,
        validation_type: str,
        metadata: Optional[Metadata] = None,
        ctx: Optional[Any] = None,
    ) -> ValidationResult:
        """Verifica si el payload cumple con las reglas del tipo especificado."""
        pass

    def Validate(
        self,
        ctx: Optional[Any],
        payload: Any,
        validation_type: str,
        metadata: Optional[Metadata] = None,
    ) -> ValidationResult:
        """Alias para compatibilidad con Go (Validate)."""
        return self.validate(payload, validation_type, metadata, ctx)

