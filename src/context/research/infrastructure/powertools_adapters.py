import os
from typing import Any, Dict, Optional, Union
from aws_lambda_powertools import Logger, Metrics
from context.research.domain.ports import ILoggerPort, IMetricsPort
from context.kit.service.logger_service import LoggerService
from context.kit.service.metrics_service import MetricsService
from context.kit.dtos.metric_unit import MetricUnit

_service_name = os.getenv("POWERTOOLS_SERVICE_NAME", "serverless-research-agent")
_namespace = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ResearchAgent")

_pt_logger = Logger(service=_service_name)
_pt_metrics = Metrics(namespace=_namespace, service=_service_name)


class PowertoolsLoggerAdapter(ILoggerPort, LoggerService):
    """Adapter wrapping AWS Lambda Powertools Logger, implementing LoggerService & ILoggerPort."""

    def __init__(self, pt_logger: Optional[Logger] = None):
        self._logger = pt_logger or _pt_logger

    def info(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        extra = {**(details or {}), **kwargs}
        if extra:
            self._logger.info(message, extra=extra)
        else:
            self._logger.info(message)

    def warn(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        extra = {**(details or {}), **kwargs}
        if extra:
            self._logger.warning(message, extra=extra)
        else:
            self._logger.warning(message)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.warn(message, **kwargs)

    def debug(self, message: str, details: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        extra = {**(details or {}), **kwargs}
        if extra:
            self._logger.debug(message, extra=extra)
        else:
            self._logger.debug(message)

    def error(
        self,
        message: str,
        err: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        extra = {**(details or {}), **kwargs}
        if err is not None:
            extra["error"] = str(err)
        if extra:
            self._logger.error(message, extra=extra)
        else:
            self._logger.error(message)


class PowertoolsMetricsAdapter(IMetricsPort, MetricsService):
    """Adapter wrapping AWS Lambda Powertools Metrics, implementing MetricsService & IMetricsPort."""

    def __init__(self, pt_metrics: Optional[Metrics] = None):
        self._metrics = pt_metrics or _pt_metrics

    def add_dimension(self, name: str, value: str) -> None:
        self._metrics.add_dimension(name=name, value=value)

    def add_metric(self, name: str, unit: Union[MetricUnit, str], value: Union[int, float]) -> None:
        unit_str = unit.value if isinstance(unit, MetricUnit) else str(unit)
        self._metrics.add_metric(name=name, unit=unit_str, value=float(value))

    def publish_stored_metrics(self, ctx: Optional[Any] = None) -> None:
        # Powertools publishes metrics automatically via decorator @metrics.log_metrics
        pass
