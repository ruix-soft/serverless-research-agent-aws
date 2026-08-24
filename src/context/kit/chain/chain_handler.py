from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C")


class Step(Generic[I, O, C], ABC):
    """
    Step define el contrato para la lógica específica de un paso en la cadena de responsabilidad.
    Traducción de Step[I, O, C] interface de Go a Python.
    """

    @abstractmethod
    def execute(self, input_dto: I, shared_context: C, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        """Contiene la lógica de negocio del paso."""
        pass

    def Execute(self, ctx: Optional[Any], input_dto: I, shared_context: C) -> Result[O, DomainError]:
        """Alias para compatibilidad con Go (Execute)."""
        return self.execute(input_dto, shared_context, ctx)

    def should_continue(self, output: O, input_dto: I, shared_context: C) -> bool:
        """Decide si se llama al siguiente eslabón. Por defecto es True."""
        return True

    def ShouldContinue(self, output: O, input_dto: I, shared_context: C) -> bool:
        """Alias para compatibilidad con Go (ShouldContinue)."""
        return self.should_continue(output, input_dto, shared_context)

    def name(self) -> str:
        """Retorna el nombre del paso (útil para logs/debugging)."""
        return self.__class__.__name__

    def Name(self) -> str:
        """Alias para compatibilidad con Go (Name)."""
        return self.name()


class BaseChainStep(Generic[I, O, C], Step[I, O, C]):
    """
    BaseChainStep es una clase base auxiliar para simplificar la implementación de Steps.
    """

    def should_continue(self, output: O, input_dto: I, shared_context: C) -> bool:
        return True

    def name(self) -> str:
        return "ChainStep"


class Handler(Generic[I, O, C]):
    """
    Handler es el orquestador de un eslabón de la cadena.
    Mantiene la referencia al siguiente handler (next) y ejecuta el paso.
    """

    def __init__(self, step: Step[I, O, C]) -> None:
        self._step = step
        self._next: Optional["Handler[I, O, C]"] = None

    @property
    def step(self) -> Step[I, O, C]:
        return self._step

    @property
    def next_handler(self) -> Optional["Handler[I, O, C]"]:
        return self._next

    def set_next(self, next_handler: "Handler[I, O, C]") -> "Handler[I, O, C]":
        """Establece el siguiente handler y lo retorna para encadenamiento fluido."""
        self._next = next_handler
        return next_handler

    def SetNext(self, next_handler: "Handler[I, O, C]") -> "Handler[I, O, C]":
        """Alias para compatibilidad con Go (SetNext)."""
        return self.set_next(next_handler)

    def handle(self, input_dto: I, shared_context: C, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        """
        Orquesta la ejecución del paso y delega al siguiente si corresponde.
        """
        result = self._step.execute(input_dto, shared_context, ctx)

        if result.is_error():
            return result

        if self._next is None:
            return result

        if self._step.should_continue(result.get(), input_dto, shared_context):
            return self._next.handle(input_dto, shared_context, ctx)

        return result

    def Handle(self, ctx: Optional[Any], input_dto: I, shared_context: C) -> Result[O, DomainError]:
        """Alias para compatibilidad con Go (Handle)."""
        return self.handle(input_dto, shared_context, ctx)


def new_handler(step: Step[I, O, C]) -> Handler[I, O, C]:
    """Constructor helper NewHandler."""
    return Handler(step)


def NewHandler(step: Step[I, O, C]) -> Handler[I, O, C]:
    """Alias Go-style para new_handler."""
    return new_handler(step)

