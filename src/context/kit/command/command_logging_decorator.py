import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.logger_service import LoggerService

I = TypeVar("I")
O = TypeVar("O")


class CommandLoggingDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandLoggingDecorator envuelve un Command para agregar logs de inicio, fin y errores.
    """

    def __init__(self, base: Handler[I, O], logger: LoggerService) -> None:
        self._base = base
        self._logger = logger

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandLoggingDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        cmd_type = self.command_type()

        self._logger.info(f"[{cmd_type}] Executing...", {"payload": payload})

        start_time = time.perf_counter()

        result = self._base.execute(payload, ctx)

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if result.is_error():
            err = result.get_error()
            err_data = err.to_primitives() if hasattr(err, "to_primitives") else str(err)
            self._logger.error(
                f"[{cmd_type}] Execution failed.",
                err=err,
                details={"duration_ms": duration_ms, "error_data": err_data},
            )
        else:
            self._logger.info(
                f"[{cmd_type}] Executed successfully.",
                {"duration_ms": duration_ms, "result": result.get()},
            )

        return result


def new_command_logging_decorator(base: Handler[I, O], logger: LoggerService) -> CommandLoggingDecorator[I, O]:
    return CommandLoggingDecorator(base, logger)


def NewCommandLoggingDecorator(base: Handler[I, O], logger: LoggerService) -> CommandLoggingDecorator[I, O]:
    return new_command_logging_decorator(base, logger)

