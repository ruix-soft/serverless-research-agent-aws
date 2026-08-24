from abc import ABC, abstractmethod
from typing import Optional, Union, Any
from context.kit.dtos.metric_unit import MetricUnit


class MetricsService(ABC):
    """
    MetricsService define el contrato para recolectar y publicar métricas.
    Traducción de MetricsService interface de Go a Python.
    """

    @abstractmethod
    def add_dimension(self, name: str, value: str) -> None:
        """Agrega una dimensión / etiqueta para las métricas."""
        pass

    def AddDimension(self, name: str, value: str) -> None:
        """Alias para compatibilidad con Go (AddDimension)."""
        self.add_dimension(name, value)

    @abstractmethod
    def add_metric(
        self,
        name: str,
        unit: Union[MetricUnit, str],
        value: Union[int, float],
    ) -> None:
        """Agrega una nueva métrica."""
        pass

    def AddMetric(
        self,
        name: str,
        unit: Union[MetricUnit, str],
        value: Union[int, float],
    ) -> None:
        """Alias para compatibilidad con Go (AddMetric)."""
        self.add_metric(name, unit, value)

    @abstractmethod
    def publish_stored_metrics(self, ctx: Optional[Any] = None) -> None:
        """Publica todas las métricas almacenadas."""
        pass

    def PublishStoredMetrics(self, ctx: Optional[Any] = None) -> None:
        """Alias para compatibilidad con Go (PublishStoredMetrics)."""
        self.publish_stored_metrics(ctx)

