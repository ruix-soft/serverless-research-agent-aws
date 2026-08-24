from typing import Optional, Dict, Any
from context.kit.errors.domain_error import DomainError


class ValidationError(DomainError):
    """
    Error de dominio de tipo 'validation'.
    Equivalente al status HTTP 400 (Bad Request) o 422 (Unprocessable Entity).
    """

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Any] = None,
    ) -> None:
        msg = message if message else "Validation failed"
        attributes: Optional[Dict[str, Any]] = None
        if details is not None:
            attributes = {"details": details}

        super().__init__(
            err_type="validation",
            message=msg,
            attributes=attributes,
        )


def new_validation_error(
    message: str = "",
    details: Optional[Any] = None,
) -> DomainError:
    """
    Crea un error de dominio de tipo 'validation'.
    Equivalente a NewValidationError(message string, details any).
    """
    return ValidationError(message=message, details=details)


def NewValidationError(
    message: str = "",
    details: Optional[Any] = None,
) -> DomainError:
    """Alias Go-style para new_validation_error."""
    return new_validation_error(message=message, details=details)

