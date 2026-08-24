from typing import Optional, Dict, Any
from context.kit.errors.domain_error import DomainError


class NotFoundError(DomainError):
    """
    Error de dominio de tipo 'not_found'.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        resource: str = "",
        id: Optional[Any] = None,
    ) -> None:
        msg = message if message else "Resource not found"
        attributes: Dict[str, Any] = {}
        if resource:
            attributes["resource"] = resource
        if id is not None and id != "" and id != 0:
            attributes["id"] = id

        super().__init__(
            err_type="not_found",
            message=msg,
            attributes=attributes,
        )


def new_not_found_error(
    message: str = "",
    resource: str = "",
    id: Optional[Any] = None,
) -> DomainError:
    """
    Crea un error de dominio de tipo 'not_found'.
    Equivalente a NewNotFoundError(message string, resource string, id any).
    """
    return NotFoundError(message=message, resource=resource, id=id)


def NewNotFoundError(
    message: str = "",
    resource: str = "",
    id: Optional[Any] = None,
) -> DomainError:
    """Alias Go-style para new_not_found_error."""
    return new_not_found_error(message=message, resource=resource, id=id)

