from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional, Any


class CacheMissError(Exception):
    """Error estándar cuando una clave no existe en caché."""
    pass


ErrCacheMiss = CacheMissError("cache: key not found")


class CacheService(ABC):
    """
    CacheService define el contrato para sistemas de caché.
    """

    @abstractmethod
    def get(self, key: str, ctx: Optional[Any] = None) -> Any:
        """Recupera un valor del caché o lanza CacheMissError si no existe."""
        pass

    def Get(self, ctx: Optional[Any], key: str, dest: Any = None) -> Any:
        """Alias para compatibilidad con Go (Get)."""
        return self.get(key, ctx)

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
        ctx: Optional[Any] = None,
    ) -> None:
        """Guarda un valor en caché con un tiempo de vida (TTL)."""
        pass

    def Set(
        self,
        ctx: Optional[Any],
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Alias para compatibilidad con Go (Set)."""
        self.set(key, value, ttl, ctx)

    @abstractmethod
    def invalidate(self, key: str, ctx: Optional[Any] = None) -> None:
        """Elimina una entrada específica de caché."""
        pass

    def Invalidate(self, ctx: Optional[Any], key: str) -> None:
        """Alias para compatibilidad con Go (Invalidate)."""
        self.invalidate(key, ctx)

    def invalidate_by_prefix(self, prefix: str, ctx: Optional[Any] = None) -> None:
        """Elimina múltiples entradas basadas en un prefijo."""
        pass

    def InvalidateByPrefix(self, ctx: Optional[Any], prefix: str) -> None:
        """Alias para compatibilidad con Go (InvalidateByPrefix)."""
        self.invalidate_by_prefix(prefix, ctx)

