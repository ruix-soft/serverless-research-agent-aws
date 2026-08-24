from typing import Optional, Dict, Any
from context.kit.errors.domain_error import DomainError


class AuthorizationError(DomainError):
    """
    Error de dominio de tipo 'authorization'.
    """

    def __init__(
        self,
        message: str = "Not authorized",
        status: int = 403,
        reason: str = "",
    ) -> None:
        msg = message if message else "Not authorized"
        attributes: Dict[str, Any] = {}
        if status > 0:
            attributes["status"] = status
        if reason:
            attributes["reason"] = reason

        super().__init__(
            err_type="authorization",
            message=msg,
            attributes=attributes,
        )


def new_authorization_error(
    message: str = "",
    status: int = 0,
    reason: str = "",
) -> DomainError:
    """
    Crea un error de dominio de tipo 'authorization'.
    Equivalente a NewAuthorizationError(message string, status int, reason string).
    """
    return AuthorizationError(message=message, status=status, reason=reason)


def NewAuthorizationError(
    message: str = "",
    status: int = 0,
    reason: str = "",
) -> DomainError:
    """Alias Go-style para new_authorization_error."""
    return new_authorization_error(message=message, status=status, reason=reason)

