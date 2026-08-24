import json
from typing import Dict, Any, Union
from datetime import datetime
from context.kit.dtos.domain_event import DomainEvent


class DomainEventSerializer:
    """
    DomainEventSerializer convierte eventos de dominio a formatos serializables (JSON / Envelope).
    Traducción de DomainEventSerializer / SerializeDomainEvent de Go a Python.
    """

    @staticmethod
    def to_envelope(event: DomainEvent) -> Dict[str, Any]:
        """
        Construye la estructura de envelope {'data': {...}} para el evento.
        """
        occurred_on = event.occurred_on()
        if isinstance(occurred_on, datetime):
            occurred_on_str = occurred_on.isoformat()
        else:
            occurred_on_str = str(occurred_on)

        return {
            "data": {
                "id": event.event_id(),
                "type": event.event_name(),
                "occurredOn": occurred_on_str,
                "aggregateId": event.aggregate_id(),
                "attributes": event.to_primitives(),
            }
        }

    @staticmethod
    def serialize(event: DomainEvent) -> str:
        """
        Convierte un evento de dominio a un string JSON.
        Equivalente a DomainEventSerializer.serialize(event).
        """
        envelope = DomainEventSerializer.to_envelope(event)
        return json.dumps(envelope, ensure_ascii=False)

    @staticmethod
    def deserialize(json_str: str) -> Dict[str, Any]:
        """
        Deserializa un string JSON de envelope de evento a diccionario.
        """
        return json.loads(json_str)


def serialize_domain_event(event: DomainEvent) -> str:
    """
    Convierte un evento de dominio a un string JSON.
    Equivalente a SerializeDomainEvent(event DomainEvent).
    """
    return DomainEventSerializer.serialize(event)


def SerializeDomainEvent(event: DomainEvent) -> str:
    """Alias Go-style para serialize_domain_event."""
    return serialize_domain_event(event)

