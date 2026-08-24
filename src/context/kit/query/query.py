from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

I = TypeVar("I")
O = TypeVar("O")


class Query(Generic[I, O], ABC):
    """
    Query define la interfaz para realizar consultas de datos (CQRS).
    I = Input (Payload, ej: filtros, IDs)
    O = Output (Resultado esperado)
    Traducción de Query[I any, O any] de Go a Python.
    """

    def query_type(self) -> str:
        """Retorna el identificador de la consulta (opcional)."""
        return getattr(self, "_query_type", "")

    def Type(self) -> str:
        """Alias para compatibilidad con Go (Type)."""
        return self.query_type()

    def metadata(self) -> Optional[Metadata]:
        """Retorna la información de contexto/auditoría (opcional)."""
        return getattr(self, "_metadata", None)

    def Metadata(self) -> Optional[Metadata]:
        """Alias para compatibilidad con Go (Metadata)."""
        return self.metadata()

    @abstractmethod
    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        """
        Ejecuta la consulta. Retorna Result[O, DomainError].
        """
        pass

    def Execute(self, ctx: Any, payload: I) -> Result[O, DomainError]:
        """Alias Go-style con orden de argumentos (ctx, payload)."""
        return self.execute(payload, ctx)

    def handle(self, payload: I) -> Result[O, DomainError]:
        """Alias handle() para compatibilidad con controladores."""
        return self.execute(payload)


class BaseQuery:
    """
    BaseQuery es una clase auxiliar para ser heredada o compuesta en consultas concretas.
    """

    def __init__(
        self,
        query_type: str = "",
        metadata: Optional[Metadata] = None,
    ) -> None:
        self._query_type = query_type
        self._metadata = metadata

    @property
    def query_type_name(self) -> str:
        return self._query_type

    def query_type(self) -> str:
        return self._query_type

    def Type(self) -> str:
        return self._query_type

    def metadata(self) -> Optional[Metadata]:
        return self._metadata

    def Metadata(self) -> Optional[Metadata]:
        return self._metadata

    def __repr__(self) -> str:
        return f"BaseQuery(query_type={self._query_type!r}, metadata={self._metadata!r})"


def new_base_query(query_type: str, metadata: Optional[Metadata] = None) -> BaseQuery:
    """Constructor helper NewBaseQuery."""
    return BaseQuery(query_type=query_type, metadata=metadata)


def NewBaseQuery(query_type: str, metadata: Optional[Metadata] = None) -> BaseQuery:
    """Alias Go-style para new_base_query."""
    return new_base_query(query_type=query_type, metadata=metadata)

