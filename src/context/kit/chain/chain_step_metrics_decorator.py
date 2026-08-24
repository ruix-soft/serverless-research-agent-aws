import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.chain.chain_handler import Step
from context.kit.dtos.metric_unit import MetricUnit
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.metrics_service import MetricsService

I = TypeVar("I")
O = TypeVar("O")
C = TypeVar("C")


class StepMetricsDecorator(Generic[I, O, C], Step[I, O, C]):
    """
    StepMetricsDecorator envuelve un Chain Step para capturar métricas automáticas:
    Latencia, Invocaciones y Errores.
    """

    def __init__(self, base: Step[I, O, C], metrics: MetricsService) -> None:
        self._base = base
        self._metrics = metrics

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
        self._metrics.add_dimension("chain_handler", handler_name)

        start_time = time.perf_counter()
        try:
            result = self._base.execute(input_dto, shared_context, ctx)

            self._metrics.add_metric("invocations", MetricUnit.COUNT, 1)
            if result.is_error():
                self._metrics.add_metric("errors", MetricUnit.COUNT, 1)

            return result
        finally:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            self._metrics.add_metric("latency", MetricUnit.MILLISECONDS, latency_ms)
            try:
                self._metrics.publish_stored_metrics(ctx)
            except Exception:
                pass


def new_step_metrics_decorator(base: Step[I, O, C], metrics: MetricsService) -> StepMetricsDecorator[I, O, C]:
    return StepMetricsDecorator(base, metrics)


def NewStepMetricsDecorator(base: Step[I, O, C], metrics: MetricsService) -> StepMetricsDecorator[I, O, C]:
    return new_step_metrics_decorator(base, metrics)

