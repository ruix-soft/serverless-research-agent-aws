import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.metric_unit import MetricUnit
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.metrics_service import MetricsService

I = TypeVar("I")
O = TypeVar("O")


class CommandMetricsDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandMetricsDecorator envuelve un Command para capturar métricas automáticas.
    """

    def __init__(self, base: Handler[I, O], metrics: MetricsService) -> None:
        self._base = base
        self._metrics = metrics

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandMetricsDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        cmd_type = self.command_type() or "UnknownCommand"
        self._metrics.add_dimension("command", cmd_type)

        start_time = time.perf_counter()
        try:
            result = self._base.execute(payload, ctx)

            if result.is_error():
                self._metrics.add_metric("errors", MetricUnit.COUNT, 1)
            else:
                self._metrics.add_metric("invocations", MetricUnit.COUNT, 1)

            return result
        finally:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            self._metrics.add_metric("latency", MetricUnit.MILLISECONDS, latency_ms)
            try:
                self._metrics.publish_stored_metrics(ctx)
            except Exception:
                pass

    def handle(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        return self.execute(payload, ctx)


def new_command_metrics_decorator(base: Handler[I, O], metrics: MetricsService) -> CommandMetricsDecorator[I, O]:
    return CommandMetricsDecorator(base, metrics)


def NewCommandMetricsDecorator(base: Handler[I, O], metrics: MetricsService) -> CommandMetricsDecorator[I, O]:
    return new_command_metrics_decorator(base, metrics)

