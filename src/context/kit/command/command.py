from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

I = TypeVar("I")
O = TypeVar("O")


class Handler(Generic[I, O], ABC):
    """
    Handler define la interfaz para ejecutar casos de uso de comandos (CQRS).
    I = Input (Payload)
    O = Output (Respuesta exitosa)
    Traducción de Handler[I any, O any] de Go a Python.
    """

    def command_type(self) -> str:
        """Retorna el identificador del comando (opcional)."""
        return getattr(self, "_cmd_type", "")

    def Type(self) -> str:
        """Alias para compatibilidad con Go (Type)."""
        return self.command_type()

    def metadata(self) -> Optional[Metadata]:
        """Retorna la información de auditoría/metadatos (opcional)."""
        return getattr(self, "_metadata", None)

    def Metadata(self) -> Optional[Metadata]:
        """Alias para compatibilidad con Go (Metadata)."""
        return self.metadata()

    @abstractmethod
    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        """
        Ejecuta la lógica del comando.
        Retorna Result[O, DomainError].
        """
        pass

    def Execute(self, ctx: Any, payload: I) -> Result[O, DomainError]:
        """
        Alias Go-style con orden de argumentos (ctx, payload).
        """
        return self.execute(payload, ctx)

    def handle(self, payload: I) -> Result[O, DomainError]:
        """
        Alias handle() para compatibilidad con la interfaz de controladores.
        """
        return self.execute(payload)


# Alias CommandHandler para Handler
CommandHandler = Handler


class BaseHandler:
    """
    BaseHandler es una clase auxiliar para ser heredada o compuesta en comandos concretos.
    Ahorra tener que implementar command_type() y metadata() manualmente.
    Traducción de BaseHandler struct de Go a Python.
    """

    def __init__(
        self,
        cmd_type: str = "",
        metadata: Optional[Metadata] = None,
        command_type: Optional[str] = None,
    ) -> None:
        self._cmd_type = command_type if command_type is not None else cmd_type
        self._metadata = metadata

    @property
    def cmd_type(self) -> str:
        return self._cmd_type

    def command_type(self) -> str:
        return self._cmd_type

    def Type(self) -> str:
        """Alias para compatibilidad con Go (Type)."""
        return self._cmd_type

    @property
    def metadata_info(self) -> Optional[Metadata]:
        return self._metadata

    def metadata(self) -> Optional[Metadata]:
        return self._metadata

    def Metadata(self) -> Optional[Metadata]:
        """Alias para compatibilidad con Go (Metadata)."""
        return self._metadata

    def __repr__(self) -> str:
        return f"BaseHandler(cmd_type={self._cmd_type!r}, metadata={self._metadata!r})"


# Alias BaseCommand para BaseHandler
BaseCommand = BaseHandler


# --- CONSTRUCTORES HELPER (traducción directa de Go) ---


def new_base_command(cmd_type: str, metadata: Optional[Metadata] = None) -> BaseHandler:
    """
    Constructor helper.
    Equivalente a NewBaseCommand(cmdType string, metadata dtos.Metadata).
    """
    return BaseHandler(cmd_type=cmd_type, metadata=metadata)


def NewBaseCommand(cmd_type: str, metadata: Optional[Metadata] = None) -> BaseHandler:
    """Alias Go-style para new_base_command."""
    return new_base_command(cmd_type=cmd_type, metadata=metadata)

