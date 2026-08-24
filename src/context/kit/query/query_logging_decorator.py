import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.logger_service import LoggerService

I = TypeVar("I")
O = TypeVar("O")


class QueryLoggingDecorator(Generic[I, O], Query[I, O]):
    """
    QueryLoggingDecorator envuelve una Query para agregar logs de inicio, fin y errores.
    """

    def __init__(self, base: Query[I, O], logger: LoggerService) -> None:
        self._base = base
        self._logger = logger

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryLoggingDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        q_type = self.query_type()

        self._logger.info(f"[{q_type}] Executing...", {"payload": payload})

        start_time = time.perf_counter()

        result = self._base.execute(payload, ctx)

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if result.is_error():
            err = result.get_error()
            err_data = err.to_primitives() if hasattr(err, "to_primitives") else str(err)
            self._logger.error(
                f"[{q_type}] Execution failed.",
                err=err,
                details={"duration_ms": duration_ms, "error_data": err_data},
            )
        else:
            self._logger.info(
                f"[{q_type}] Executed successfully.",
                {"duration_ms": duration_ms, "result": result.get()},
            )

        return result


def new_query_logging_decorator(base: Query[I, O], logger: LoggerService) -> QueryLoggingDecorator[I, O]:
    return QueryLoggingDecorator(base, logger)


def NewQueryLoggingDecorator(base: Query[I, O], logger: LoggerService) -> QueryLoggingDecorator[I, O]:
    return new_query_logging_decorator(base, logger)

