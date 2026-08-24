from abc import ABC, abstractmethod
from typing import List, Optional, Any
from context.kit.dtos.domain_event import DomainEvent


class DomainEventSubscriber(ABC):
    """
    DomainEventSubscriber define el contrato para cualquier suscriptor de eventos de dominio.
    """

    @abstractmethod
    def subscribed_to(self) -> List[str]:
        """Retorna la lista de nombres de eventos que este suscriptor escucha."""
        pass

    def SubscribedTo(self) -> List[str]:
        """Alias para compatibilidad con Go (SubscribedTo)."""
        return self.subscribed_to()

    @abstractmethod
    def on(self, event: DomainEvent, ctx: Optional[Any] = None) -> None:
        """Ejecuta la lógica cuando ocurre el evento de dominio."""
        pass

    def On(self, ctx: Optional[Any], event: DomainEvent) -> None:
        """Alias para compatibilidad con Go (On)."""
        self.on(event, ctx)

