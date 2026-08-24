from typing import Optional, Any
from context.kit.errors.domain_error import DomainError, new_domain_error


def as_domain_error(err: Any) -> DomainError:
    """
    Intenta convertir un error estándar a DomainError.
    Si no es un DomainError, crea un DomainError genérico de tipo 'unknown_error'.
    Traducción de AsDomainError de Go a Python.
    """
    if err is None:
        return new_domain_error("unknown_error", "Unknown error occurred", None)

    if isinstance(err, DomainError):
        return err

    if isinstance(err, BaseException):
        return new_domain_error("unknown_error", str(err), None)

    return new_domain_error("unknown_error", str(err), None)


def AsDomainError(err: Any) -> DomainError:
    """Alias Go-style para as_domain_error."""
    return as_domain_error(err)

