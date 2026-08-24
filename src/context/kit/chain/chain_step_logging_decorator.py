import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.chain.chain_handler import Step
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.logger_service import LoggerService

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C")


class StepLoggingDecorator(Generic[I, O, C], Step[I, O, C]):
    """
    StepLoggingDecorator envuelve un Chain Step para agregar logs automáticos de inicio, éxito y error.
    Traducción de StepLoggingDecorator de Go a Python.
    """

    def __init__(self, base: Step[I, O, C], logger: LoggerService) -> None:
        self._base = base
        self._logger = logger

    def name(self) -> str:
        return self._base.name()

    def Name(self) -> str:
        return self._base.Name()

    def should_continue(self, output: O, input_dto: I, shared_context: C) -> bool:
        return self._base.should_continue(output, input_dto, shared_context)

    def ShouldContinue(self, output: O, input_dto: I, shared_context: C) -> bool:
        return self._base.ShouldContinue(output, input_dto, shared_context)

    def execute(self, input_dto: I, shared_context: C, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        handler_name = self.name()

        self._logger.info("Handling...", {
            "handlerName": handler_name,
            "input": input_dto,
            "context": shared_context,
        })

        start_time = time.perf_counter()

        result = self._base.execute(input_dto, shared_context, ctx)

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if result.is_ok():
            self._logger.info("Handled successfully.", {
                "handlerName": handler_name,
                "duration_ms": duration_ms,
                "result": result.get(),
            })
        else:
            err = result.get_error()
            err_primitives = err.to_primitives() if hasattr(err, "to_primitives") else str(err)
            self._logger.warn("Handled with domain error.", {
                "handlerName": handler_name,
                "duration_ms": duration_ms,
                "error": err_primitives,
            })

        return result


def new_step_logging_decorator(base: Step[I, O, C], logger: LoggerService) -> StepLoggingDecorator[I, O, C]:
    return StepLoggingDecorator(base, logger)


def NewStepLoggingDecorator(base: Step[I, O, C], logger: LoggerService) -> StepLoggingDecorator[I, O, C]:
    return new_step_logging_decorator(base, logger)

