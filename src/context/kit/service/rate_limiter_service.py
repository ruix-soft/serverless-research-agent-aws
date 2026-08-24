from abc import ABC, abstractmethod
from typing import Optional, Any


class RateLimiterService(ABC):
    """
    RateLimiterService define el contrato para limitar la frecuencia de acciones.
    """

    @abstractmethod
    def allow(
        self,
        key: str,
        limit: int,
        window_ms: int,
        ctx: Optional[Any] = None,
    ) -> bool:
        """Determina si una acción identificada por 'key' está permitida."""
        pass

    def Allow(
        self,
        ctx: Optional[Any],
        key: str,
        limit: int,
        window_ms: int,
    ) -> bool:
        """Alias para compatibilidad con Go (Allow)."""
        return self.allow(key, limit, window_ms, ctx)

