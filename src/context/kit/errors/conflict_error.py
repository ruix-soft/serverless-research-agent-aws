from typing import Optional, Dict, Any
from context.kit.errors.domain_error import DomainError


class ConflictError(DomainError):
    """
    Error de dominio de tipo 'conflict'.
    Útil para duplicados (Unique Constraint violations) o conflictos de estado.
    """

    def __init__(
        self,
        message: str = "Conflict",
        details: Optional[Any] = None,
    ) -> None:
        msg = message if message else "Conflict"
        attributes: Optional[Dict[str, Any]] = None
        if details is not None:
            attributes = {"details": details}

        super().__init__(
            err_type="conflict",
            message=msg,
            attributes=attributes,
        )


def new_conflict_error(
    message: str = "",
    details: Optional[Any] = None,
) -> DomainError:
    """
    Crea un error de dominio de tipo 'conflict'.
    Equivalente a NewConflictError(message string, details any).
    """
    return ConflictError(message=message, details=details)


def NewConflictError(
    message: str = "",
    details: Optional[Any] = None,
) -> DomainError:
    """Alias Go-style para new_conflict_error."""
    return new_conflict_error(message=message, details=details)

