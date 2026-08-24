from typing import Generic, TypeVar, Optional, Any
from context.kit.chain.chain_handler import Step
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.tracer_service import TracerService

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C")


class StepTracingDecorator(Generic[I, O, C], Step[I, O, C]):
    """
    StepTracingDecorator envuelve un Chain Step para generar trazas distribuidas.
    """

    def __init__(self, base: Step[I, O, C], tracer: TracerService) -> None:
        self._base = base
        self._tracer = tracer

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

        parent_seg = self._tracer.get_segment(ctx)
        subsegment = parent_seg.add_new_subsegment(handler_name) if parent_seg else None
        child_ctx = self._tracer.set_segment(ctx, subsegment) if subsegment else ctx

        err_for_trace = None
        try:
            result = self._base.execute(input_dto, shared_context, child_ctx)

            if subsegment:
                if result.is_ok():
                    subsegment.add_metadata("result.value", result.get())
                else:
                    domain_err = result.get_error()
                    err_meta = domain_err.to_primitives() if hasattr(domain_err, "to_primitives") else str(domain_err)
                    subsegment.add_metadata("result.error", err_meta)

            return result
        except Exception as exc:
            err_for_trace = exc
            raise
        finally:
            if subsegment:
                subsegment.close(err_for_trace)


def new_step_tracing_decorator(base: Step[I, O, C], tracer: TracerService) -> StepTracingDecorator[I, O, C]:
    return StepTracingDecorator(base, tracer)


def NewStepTracingDecorator(base: Step[I, O, C], tracer: TracerService) -> StepTracingDecorator[I, O, C]:
    return new_step_tracing_decorator(base, tracer)

