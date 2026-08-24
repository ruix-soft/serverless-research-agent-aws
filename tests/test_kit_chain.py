import pytest
import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.chain import (
    Step,
    BaseChainStep,
    Handler,
    NewHandler,
    new_handler,
    ChainBuilder,
    NewBuilder,
    new_chain_builder,
    StepLoggingDecorator,
    StepMetricsDecorator,
    StepTracingDecorator,
)
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, NewDomainError
from context.kit.service.logger_service import LoggerService
from context.kit.service.metrics_service import MetricsService
from context.kit.service.tracer_service import TracerService, Segment


class DummyLogger(LoggerService):
    def __init__(self):
        self.logs = []

    def info(self, message: str, details=None):
        self.logs.append(("INFO", message, details))

    def warn(self, message: str, details=None):
        self.logs.append(("WARN", message, details))

    def debug(self, message: str, details=None):
        self.logs.append(("DEBUG", message, details))

    def error(self, message: str, err=None, details=None):
        self.logs.append(("ERROR", message, err, details))


class DummyMetrics(MetricsService):
    def __init__(self):
        self.dimensions = {}
        self.metrics = []

    def add_dimension(self, name: str, value: str):
        self.dimensions[name] = value

    def add_metric(self, name: str, unit, value: float):
        self.metrics.append((name, unit, value))

    def publish_stored_metrics(self, ctx=None):
        pass


class DummySegment(Segment):
    def __init__(self, name: str):
        self.name_str = name
        self.meta = {}
        self.closed = False

    def add_new_subsegment(self, name: str) -> Segment:
        return DummySegment(name)

    def add_metadata(self, key: str, value: Any):
        self.meta[key] = value

    def close(self, err=None):
        self.closed = True


class DummyTracer(TracerService):
    def __init__(self):
        self.current_seg = DummySegment("root")

    def get_segment(self, ctx=None):
        return self.current_seg

    def set_segment(self, ctx, segment: Segment):
        return ctx


class StepOne(BaseChainStep[int, int, dict]):
    def name(self) -> str:
        return "StepOne"

    def execute(self, input_dto: int, shared_context: dict, ctx=None) -> Result[int, DomainError]:
        shared_context["step1"] = True
        return Result.ok(input_dto + 10)


class StepTwo(BaseChainStep[int, int, dict]):
    def name(self) -> str:
        return "StepTwo"

    def execute(self, input_dto: int, shared_context: dict, ctx=None) -> Result[int, DomainError]:
        shared_context["step2"] = True
        return Result.ok(input_dto * 2)


def test_chain_builder_execution():
    builder = NewBuilder()
    builder.add_handler(StepOne()).add_handler(StepTwo())

    shared_ctx = {}
    result = builder.execute(5, shared_ctx)

    assert result.is_ok() is True
    # StepOne runs on 5 -> returns 15, then StepTwo runs on input 5 -> returns 10
    assert result.get() == 10
    assert shared_ctx["step1"] is True
    assert shared_ctx["step2"] is True


def test_chain_decorators():
    logger = DummyLogger()
    metrics = DummyMetrics()
    tracer = DummyTracer()

    step = StepOne()
    logged = StepLoggingDecorator(step, logger)
    metered = StepMetricsDecorator(logged, metrics)
    traced = StepTracingDecorator(metered, tracer)

    shared_ctx = {}
    res = traced.execute(10, shared_ctx)

    assert res.is_ok() is True
    assert res.get() == 20
    assert len(logger.logs) >= 2
    assert len(metrics.metrics) >= 2

