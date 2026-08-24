import time
from typing import TypeVar, Optional, Any
from app.controllers.base import IHandler
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class LoggingDecorator(IHandler[InputDTO, OutputDTO]):
    """Decorator to apply structured logging across Command and Query handlers."""

    def __init__(self, handler: IHandler[InputDTO, OutputDTO], logger: Any, handler_name: Optional[str] = None):
        self._handler = handler
        self._logger = logger
        self._handler_name = handler_name or handler.__class__.__name__

    def handle(self, input_dto: InputDTO, ctx: Optional[Any] = None) -> Result[OutputDTO, DomainError]:
        start_time = time.perf_counter()
        if hasattr(self._logger, "info"):
            try:
                self._logger.info(
                    f"Executing {self._handler_name}",
                    details={"handler": self._handler_name, "input": str(input_dto)}
                )
            except TypeError:
                self._logger.info(
                    f"Executing {self._handler_name}",
                    extra={"handler": self._handler_name, "input": str(input_dto)}
                )

        try:
            if ctx is not None:
                try:
                    result = self._handler.handle(input_dto, ctx)
                except TypeError:
                    result = self._handler.handle(input_dto)
            else:
                try:
                    result = self._handler.handle(input_dto)
                except TypeError:
                    result = self._handler.handle(input_dto, ctx)
            duration_ms = (time.perf_counter() - start_time) * 1000

            if result.is_ok():
                if hasattr(self._logger, "info"):
                    try:
                        self._logger.info(
                            f"{self._handler_name} succeeded in {duration_ms:.2f}ms",
                            details={"handler": self._handler_name, "duration_ms": duration_ms}
                        )
                    except TypeError:
                        self._logger.info(
                            f"{self._handler_name} succeeded in {duration_ms:.2f}ms",
                            extra={"handler": self._handler_name, "duration_ms": duration_ms}
                        )
            else:
                err = result.get_error()
                err_dict = err.to_primitives() if hasattr(err, "to_primitives") else str(err)
                if hasattr(self._logger, "error"):
                    try:
                        self._logger.error(
                            f"{self._handler_name} failed in {duration_ms:.2f}ms: {err.message}",
                            err=err,
                            details={
                                "handler": self._handler_name,
                                "duration_ms": duration_ms,
                                "error": err_dict
                            }
                        )
                    except TypeError:
                        self._logger.error(
                            f"{self._handler_name} failed in {duration_ms:.2f}ms: {err.message}",
                            extra={
                                "handler": self._handler_name,
                                "duration_ms": duration_ms,
                                "error": err_dict
                            }
                        )
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if hasattr(self._logger, "error"):
                try:
                    self._logger.error(
                        f"Unhandled exception in {self._handler_name} after {duration_ms:.2f}ms: {str(e)}",
                        err=e,
                        details={"handler": self._handler_name, "duration_ms": duration_ms}
                    )
                except TypeError:
                    self._logger.error(
                        f"Unhandled exception in {self._handler_name} after {duration_ms:.2f}ms: {str(e)}",
                        extra={"handler": self._handler_name, "duration_ms": duration_ms, "exception": str(e)}
                    )
            raise e
