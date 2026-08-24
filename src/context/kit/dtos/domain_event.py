import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class DomainEvent(ABC):
    """
    DomainEvent define el contrato que todos los eventos de dominio deben cumplir.
    Traducción de la interface DomainEvent de Go a Python.
    """

    @abstractmethod
    def event_name(self) -> str:
        """Nombre único del evento de dominio."""
        pass

    def EventName(self) -> str:
        """Alias para compatibilidad con Go (EventName)."""
        return self.event_name()

    @abstractmethod
    def aggregate_id(self) -> str:
        """Identificador del agregado raíz que originó el evento."""
        pass

    def AggregateID(self) -> str:
        """Alias para compatibilidad con Go (AggregateID)."""
        return self.aggregate_id()

    @abstractmethod
    def event_id(self) -> str:
        """Identificador único UUID del evento."""
        pass

    def EventID(self) -> str:
        """Alias para compatibilidad con Go (EventID)."""
        return self.event_id()

    @abstractmethod
    def occurred_on(self) -> datetime:
        """Marca de tiempo UTC cuando ocurrió el evento."""
        pass

    def OccurredOn(self) -> datetime:
        """Alias para compatibilidad con Go (OccurredOn)."""
        return self.occurred_on()

    @abstractmethod
    def to_primitives(self) -> Dict[str, Any]:
        """Serializa el evento a tipos primitivos estándar (map / dict)."""
        pass

    def ToPrimitives(self) -> Dict[str, Any]:
        """Alias para compatibilidad con Go (ToPrimitives)."""
        return self.to_primitives()


class BaseDomainEvent(DomainEvent):
    """
    BaseDomainEvent clase base para ser heredada o compuesta en eventos concretos.
    Traducción de BaseDomainEvent struct de Go a Python.
    """

    def __init__(
        self,
        event_name: str,
        aggregate_id: str,
        event_id: Optional[str] = None,
        occurred_on: Optional[datetime] = None,
    ) -> None:
        self._event_name = event_name
        self._aggregate_id = aggregate_id
        self._event_id = event_id or str(uuid.uuid4())
        self._occurred_on = occurred_on or datetime.now(timezone.utc)

    def event_name(self) -> str:
        return self._event_name

    def aggregate_id(self) -> str:
        return self._aggregate_id

    def event_id(self) -> str:
        return self._event_id

    def occurred_on(self) -> datetime:
        return self._occurred_on

    def to_primitives(self) -> Dict[str, Any]:
        return {
            "event_name": self._event_name,
            "aggregate_id": self._aggregate_id,
            "event_id": self._event_id,
            "occurred_on": self._occurred_on.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Alias para to_primitives."""
        return self.to_primitives()

    @classmethod
    def from_primitives(cls, data: Dict[str, Any]) -> "BaseDomainEvent":
        """
        Rehidrata un BaseDomainEvent a partir de un diccionario de primitivos.
        """
        event_name = (
            data.get("event_name")
            or data.get("eventName")
            or data.get("EventName")
            or ""
        )
        aggregate_id = (
            data.get("aggregate_id")
            or data.get("aggregateId")
            or data.get("AggregateID")
            or ""
        )
        event_id = (
            data.get("event_id")
            or data.get("eventId")
            or data.get("EventID")
        )

        raw_occurred = (
            data.get("occurred_on")
            or data.get("occurredOn")
            or data.get("OccurredOn")
        )
        occurred_on: Optional[datetime] = None
        if isinstance(raw_occurred, datetime):
            occurred_on = raw_occurred
        elif isinstance(raw_occurred, str) and raw_occurred:
            try:
                occurred_on = datetime.fromisoformat(raw_occurred)
            except ValueError:
                occurred_on = None

        return cls(
            event_name=event_name,
            aggregate_id=aggregate_id,
            event_id=event_id,
            occurred_on=occurred_on,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseDomainEvent):
            return False
        return (
            self._event_name == other._event_name
            and self._aggregate_id == other._aggregate_id
            and self._event_id == other._event_id
            and self._occurred_on == other._occurred_on
        )

    def __repr__(self) -> str:
        return (
            f"BaseDomainEvent(event_name={self._event_name!r}, "
            f"aggregate_id={self._aggregate_id!r}, "
            f"event_id={self._event_id!r}, "
            f"occurred_on={self._occurred_on!r})"
        )


@dataclass(frozen=True)
class DomainEventMeta:
    """
    DomainEventMeta representa la estructura mínima necesaria para identificar un evento.
    Es el equivalente en tiempo de ejecución a Pick<T, 'eventName'>.
    Útil para 'Partial Unmarshalling' (leer solo el nombre para saber a qué Handler enviarlo).
    """

    event_name: str

    @property
    def EventName(self) -> str:
        """Alias para compatibilidad con Go (EventName)."""
        return self.event_name

    @property
    def eventName(self) -> str:
        """Alias camelCase para event_name."""
        return self.event_name

    def to_dict(self) -> Dict[str, Any]:
        return {"event_name": self.event_name}

    def to_primitives(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEventMeta":
        name = (
            data.get("event_name")
            or data.get("eventName")
            or data.get("EventName")
            or ""
        )
        return cls(event_name=name)

    @classmethod
    def from_primitives(cls, data: Dict[str, Any]) -> "DomainEventMeta":
        return cls.from_dict(data)


# --- CONSTRUCTORES HELPER (traducción directa de Go) ---


def new_base_domain_event(
    event_name: str,
    aggregate_id: str,
    event_id: Optional[str] = None,
    occurred_on: Optional[datetime] = None,
) -> BaseDomainEvent:
    """
    Crea una nueva instancia de BaseDomainEvent.
    Equivalente a NewBaseDomainEvent(eventName, aggregateID string).
    """
    return BaseDomainEvent(
        event_name=event_name,
        aggregate_id=aggregate_id,
        event_id=event_id,
        occurred_on=occurred_on,
    )


def NewBaseDomainEvent(
    event_name: str,
    aggregate_id: str,
    event_id: Optional[str] = None,
    occurred_on: Optional[datetime] = None,
) -> BaseDomainEvent:
    """Alias Go-style para new_base_domain_event."""
    return new_base_domain_event(
        event_name=event_name,
        aggregate_id=aggregate_id,
        event_id=event_id,
        occurred_on=occurred_on,
    )

