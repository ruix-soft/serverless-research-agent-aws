from typing import List
from context.kit.dtos.domain_event import DomainEvent


class AggregateRoot:
    """
    AggregateRoot maneja la lista de eventos de dominio generados durante cambios de estado.
    Traducción de AggregateRoot struct de Go a Python.
    """

    def __init__(self) -> None:
        self._domain_events: List[DomainEvent] = []

    def pull_domain_events(self) -> List[DomainEvent]:
        """
        Retorna y limpia los eventos de dominio acumulados.
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def PullDomainEvents(self) -> List[DomainEvent]:
        """Alias para compatibilidad con Go (PullDomainEvents)."""
        return self.pull_domain_events()

    def record(self, event: DomainEvent) -> None:
        """
        Registra un nuevo evento de dominio.
        """
        self._domain_events.append(event)

    def Record(self, event: DomainEvent) -> None:
        """Alias para compatibilidad con Go (Record)."""
        self.record(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """Retorna una copia de los eventos sin limpiarlos."""
        return list(self._domain_events)

