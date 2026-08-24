from typing import Generic, TypeVar, Optional, Any, Union
from context.kit.chain.chain_handler import Handler, Step, new_handler
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C")


class ChainBuilder(Generic[I, O, C]):
    """
    ChainBuilder facilita la construcción fluida de una cadena de responsabilidad.
    Traducción de ChainBuilder[I, O, C] de Go a Python.
    """

    def __init__(self) -> None:
        self._first: Optional[Handler[I, O, C]] = None
        self._last: Optional[Handler[I, O, C]] = None

    @classmethod
    def new_builder(cls) -> "ChainBuilder[I, O, C]":
        return cls()

    @classmethod
    def NewBuilder(cls) -> "ChainBuilder[I, O, C]":
        return cls.new_builder()

    def add_handler(self, handler_or_step: Union[Handler[I, O, C], Step[I, O, C]]) -> "ChainBuilder[I, O, C]":
        """
        Añade un Handler o Step al final de la cadena y retorna el mismo builder (fluent API).
        """
        if isinstance(handler_or_step, Handler):
            handler = handler_or_step
        else:
            handler = new_handler(handler_or_step)

        if self._first is None:
            self._first = handler
            self._last = handler
        else:
            assert self._last is not None
            self._last.set_next(handler)
            self._last = handler

        return self

    def AddHandler(self, handler_or_step: Union[Handler[I, O, C], Step[I, O, C]]) -> "ChainBuilder[I, O, C]":
        """Alias para compatibilidad con Go (AddHandler)."""
        return self.add_handler(handler_or_step)

    def build(self) -> Handler[I, O, C]:
        """
        Finaliza la construcción y retorna el primer handler de la cadena.
        Lanza ValueError si la cadena está vacía.
        """
        if self._first is None:
            raise ValueError("ChainBuilder requires at least one handler")
        return self._first

    def Build(self) -> Handler[I, O, C]:
        """Alias para compatibilidad con Go (Build)."""
        return self.build()

    def execute(self, input_dto: I, shared_context: C, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        """
        Atajo para construir y ejecutar la cadena directamente.
        """
        return self.build().handle(input_dto, shared_context, ctx)

    def Execute(self, ctx: Optional[Any], input_dto: I, shared_context: C) -> Result[O, DomainError]:
        """Alias para compatibilidad con Go (Execute)."""
        return self.execute(input_dto, shared_context, ctx)


def new_chain_builder() -> ChainBuilder[Any, Any, Any]:
    """Constructor helper NewBuilder."""
    return ChainBuilder()


def NewBuilder() -> ChainBuilder[Any, Any, Any]:
    """Alias Go-style para new_chain_builder."""
    return new_chain_builder()

