from abc import ABC, abstractmethod
from typing import Optional, Any


class Segment(ABC):
    """
    Segment representa un segmento o subsegmento de traza distribuida (X-Ray / OpenTelemetry).
    """

    @abstractmethod
    def add_new_subsegment(self, name: str) -> "Segment":
        """Crea y retorna un nuevo subsegmento hijo."""
        pass

    def AddNewSubsegment(self, name: str) -> "Segment":
        """Alias para compatibilidad con Go (AddNewSubsegment)."""
        return self.add_new_subsegment(name)

    @abstractmethod
    def add_metadata(self, key: str, value: Any) -> None:
        """Agrega metadatos al segmento."""
        pass

    def AddMetadata(self, key: str, value: Any) -> None:
        """Alias para compatibilidad con Go (AddMetadata)."""
        self.add_metadata(key, value)

    @abstractmethod
    def close(self, err: Optional[Any] = None) -> None:
        """Cierra el segmento."""
        pass

    def Close(self, err: Optional[Any] = None) -> None:
        """Alias para compatibilidad con Go (Close)."""
        self.close(err)

    def parent(self) -> Optional["Segment"]:
        """Retorna el segmento padre si existe."""
        return None

    def Parent(self) -> Optional["Segment"]:
        """Alias para compatibilidad con Go (Parent)."""
        return self.parent()


class TracerService(ABC):
    """
    TracerService define el contrato para interactuar con el sistema de trazabilidad distribuida.
    """

    @abstractmethod
    def get_segment(self, ctx: Optional[Any] = None) -> Optional[Segment]:
        """Obtiene el segmento activo actual."""
        pass

    def GetSegment(self, ctx: Optional[Any] = None) -> Optional[Segment]:
        """Alias para compatibilidad con Go (GetSegment)."""
        return self.get_segment(ctx)

    @abstractmethod
    def set_segment(self, ctx: Optional[Any], segment: Segment) -> Any:
        """Inyecta o asocia un segmento con el contexto de ejecución."""
        pass

    def SetSegment(self, ctx: Optional[Any], segment: Segment) -> Any:
        """Alias para compatibilidad con Go (SetSegment)."""
        return self.set_segment(ctx, segment)

