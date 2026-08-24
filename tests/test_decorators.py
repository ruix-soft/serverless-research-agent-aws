import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from typing import Any
from app.controllers.base import ICommandHandler
from app.controllers.decorators.logging_decorator import LoggingDecorator
from app.controllers.decorators.metrics_decorator import MetricsDecorator
from context.research.domain.ports import ILoggerPort, IMetricsPort
from context.kit.dtos.result import Result
from context.kit.errors.validation_error import ValidationError


class DummyLogger(ILoggerPort):
    def __init__(self):
        self.logs = []

    def info(self, message: str, **kwargs: Any) -> None:
        self.logs.append(("INFO", message, kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self.logs.append(("ERROR", message, kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self.logs.append(("WARNING", message, kwargs))


class DummyMetrics(IMetricsPort):
    def __init__(self):
        self.metrics = []

    def add_metric(self, name: str, unit: str, value: float) -> None:
        self.metrics.append((name, unit, value))


class SuccessfulHandler(ICommandHandler[str, str]):
    def handle(self, input_dto: str) -> Result[str, Any]:
        return Result.ok(f"processed: {input_dto}")


class FailingHandler(ICommandHandler[str, str]):
    def handle(self, input_dto: str) -> Result[str, Any]:
        return Result.fail(ValidationError("Validation failed"))


def test_logging_decorator_success():
    logger = DummyLogger()
    handler = SuccessfulHandler()
    decorated = LoggingDecorator(handler, logger=logger, handler_name="TestHandler")

    res = decorated.handle("hello")
    assert res.is_ok() is True
    assert res.value == "processed: hello"
    assert len(logger.logs) == 2
    assert logger.logs[0][0] == "INFO"
    assert "Executing TestHandler" in logger.logs[0][1]
    assert logger.logs[1][0] == "INFO"
    assert "succeeded" in logger.logs[1][1]


def test_logging_decorator_failure():
    logger = DummyLogger()
    handler = FailingHandler()
    decorated = LoggingDecorator(handler, logger=logger, handler_name="FailHandler")

    res = decorated.handle("hello")
    assert res.is_err() is True
    assert len(logger.logs) == 2
    assert logger.logs[1][0] == "ERROR"
    assert "failed" in logger.logs[1][1]


def test_metrics_decorator_success():
    metrics = DummyMetrics()
    handler = SuccessfulHandler()
    decorated = MetricsDecorator(handler, metrics=metrics, metric_namespace="TestOp")

    res = decorated.handle("sample")
    assert res.is_ok() is True
    metric_names = [m[0] for m in metrics.metrics]
    assert "TestOp.Invocations" in metric_names
    assert "TestOp.Latency" in metric_names
    assert "TestOp.Success" in metric_names


def test_metrics_decorator_failure():
    metrics = DummyMetrics()
    handler = FailingHandler()
    decorated = MetricsDecorator(handler, metrics=metrics, metric_namespace="TestOp")

    res = decorated.handle("sample")
    assert res.is_err() is True
    metric_names = [m[0] for m in metrics.metrics]
    assert "TestOp.Invocations" in metric_names
    assert "TestOp.Latency" in metric_names
    assert "TestOp.Failure" in metric_names
