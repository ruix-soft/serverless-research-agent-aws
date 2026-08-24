import time
from typing import TypeVar, Optional, Any
from app.controllers.base import IHandler
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class MetricsDecorator(IHandler[InputDTO, OutputDTO]):
    """Decorator to publish metrics across Command and Query handlers."""

    def __init__(self, handler: IHandler[InputDTO, OutputDTO], metrics: Any, metric_namespace: Optional[str] = None):
        self._handler = handler
        self._metrics = metrics
        self._metric_name = metric_namespace or handler.__class__.__name__

    def handle(self, input_dto: InputDTO, ctx: Optional[Any] = None) -> Result[OutputDTO, DomainError]:
        start_time = time.perf_counter()
        if hasattr(self._metrics, "add_metric"):
            self._metrics.add_metric(name=f"{self._metric_name}.Invocations", unit="Count", value=1)

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

        if hasattr(self._metrics, "add_metric"):
            self._metrics.add_metric(name=f"{self._metric_name}.Latency", unit="Milliseconds", value=duration_ms)

            if result.is_ok():
                self._metrics.add_metric(name=f"{self._metric_name}.Success", unit="Count", value=1)
            else:
                self._metrics.add_metric(name=f"{self._metric_name}.Failure", unit="Count", value=1)

        return result
