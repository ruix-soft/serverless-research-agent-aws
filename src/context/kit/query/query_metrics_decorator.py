import time
from typing import Generic, TypeVar, Optional, Any
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.metric_unit import MetricUnit
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.metrics_service import MetricsService

I = TypeVar("I")
O = TypeVar("O")


class QueryMetricsDecorator(Generic[I, O], Query[I, O]):
    """
    QueryMetricsDecorator envuelve una Query para capturar métricas automáticas.
    """

    def __init__(self, base: Query[I, O], metrics: MetricsService) -> None:
        self._base = base
        self._metrics = metrics

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryMetricsDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        q_type = self.query_type() or "UnknownQuery"
        self._metrics.add_dimension("query", q_type)

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


def new_query_metrics_decorator(base: Query[I, O], metrics: MetricsService) -> QueryMetricsDecorator[I, O]:
    return QueryMetricsDecorator(base, metrics)


def NewQueryMetricsDecorator(base: Query[I, O], metrics: MetricsService) -> QueryMetricsDecorator[I, O]:
    return new_query_metrics_decorator(base, metrics)

