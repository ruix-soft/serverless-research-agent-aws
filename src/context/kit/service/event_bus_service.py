from abc import ABC, abstractmethod
from typing import List, Optional, Any
from context.kit.dtos.domain_event import DomainEvent


class EventBusService(ABC):
    """
    EventBusService define el contrato para el bus de eventos (RabbitMQ, SNS, EventBridge, In-Memory).
    """

    @abstractmethod
    def publish(self, events: List[DomainEvent], ctx: Optional[Any] = None) -> None:
        """Publica una lista de eventos de dominio."""
        pass

    def Publish(self, ctx: Optional[Any], events: List[DomainEvent]) -> None:
        """Alias para compatibilidad con Go (Publish)."""
        self.publish(events, ctx)

