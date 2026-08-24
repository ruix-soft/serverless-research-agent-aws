from typing import Optional, Dict, Any
from context.kit.errors.domain_error import DomainError


class RateLimitError(DomainError):
    """
    Error de dominio de tipo 'rate_limit'.
    """

    def __init__(
        self,
        key: str,
        limit: int,
        window_ms: int,
        retry_after_ms: int = 0,
    ) -> None:
        message = f"Rate limit exceeded for {key}"
        attributes: Dict[str, Any] = {
            "key": key,
            "limit": limit,
            "windowMs": window_ms,
        }
        if retry_after_ms > 0:
            attributes["retryAfterMs"] = retry_after_ms

        super().__init__(
            err_type="rate_limit",
            message=message,
            attributes=attributes,
        )


def new_rate_limit_error(
    key: str,
    limit: int,
    window_ms: int,
    retry_after_ms: int = 0,
) -> DomainError:
    """
    Construye un DomainError para límites de velocidad.
    Equivalente a NewRateLimitError(key string, limit int, windowMs int, retryAfterMs int).
    """
    return RateLimitError(
        key=key,
        limit=limit,
        window_ms=window_ms,
        retry_after_ms=retry_after_ms,
    )


def NewRateLimitError(
    key: str,
    limit: int,
    window_ms: int,
    retry_after_ms: int = 0,
) -> DomainError:
    """Alias Go-style para new_rate_limit_error."""
    return new_rate_limit_error(
        key=key,
        limit=limit,
        window_ms=window_ms,
        retry_after_ms=retry_after_ms,
    )

