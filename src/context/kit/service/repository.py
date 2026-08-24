from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")


class Repository(Generic[T], ABC):
    """
    Repository define el contrato genérico para persistencia.
    T representa la Entidad o Agregado.
    """

    @abstractmethod
    def query(self, query: Any, ctx: Optional[Any] = None) -> List[T]:
        """Ejecuta una consulta de lectura."""
        pass

    def Query(self, ctx: Optional[Any], query: Any) -> List[T]:
        """Alias para compatibilidad con Go (Query)."""
        return self.query(query, ctx)

    @abstractmethod
    def execute(self, query: Any, ctx: Optional[Any] = None) -> None:
        """Ejecuta una operación de escritura (INSERT, UPDATE, DELETE)."""
        pass

    def Execute(self, ctx: Optional[Any], query: Any) -> None:
        """Alias para compatibilidad con Go (Execute)."""
        self.execute(query, ctx)

    def close(self, ctx: Optional[Any] = None) -> None:
        """Cierra la conexión al repositorio."""
        pass

    def Close(self, ctx: Optional[Any] = None) -> None:
        self.close(ctx)

