import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.domain_event import (
    DomainEvent,
    BaseDomainEvent,
    DomainEventMeta,
    NewBaseDomainEvent,
    new_base_domain_event,
)


def test_base_domain_event_creation():
    event = NewBaseDomainEvent("research.started", "agg_123")
    assert event.event_name() == "research.started"
    assert event.EventName() == "research.started"
    assert event.aggregate_id() == "agg_123"
    assert event.AggregateID() == "agg_123"
    assert event.event_id() is not None
    assert event.EventID() is not None
    assert isinstance(uuid.UUID(event.event_id()), uuid.UUID)
    assert event.occurred_on() is not None
    assert event.OccurredOn() is not None
    assert isinstance(event.occurred_on(), datetime)


def test_base_domain_event_to_primitives():
    fixed_time = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)
    event = BaseDomainEvent(
        event_name="research.completed",
        aggregate_id="agg_456",
        event_id="evt_789",
        occurred_on=fixed_time,
    )
    primitives = event.to_primitives()
    assert primitives == {
        "event_name": "research.completed",
        "aggregate_id": "agg_456",
        "event_id": "evt_789",
        "occurred_on": fixed_time.isoformat(),
    }
    assert event.ToPrimitives() == primitives
    assert event.to_dict() == primitives


def test_base_domain_event_from_primitives():
    fixed_time = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)
    data = {
        "eventName": "user.registered",
        "aggregateId": "usr_999",
        "eventId": "evt_111",
        "occurredOn": fixed_time.isoformat(),
    }
    event = BaseDomainEvent.from_primitives(data)
    assert event.event_name() == "user.registered"
    assert event.aggregate_id() == "usr_999"
    assert event.event_id() == "evt_111"
    assert event.occurred_on() == fixed_time


def test_concrete_domain_event_subclass():
    class CustomResearchEvent(BaseDomainEvent):
        def __init__(self, aggregate_id: str, topic: str):
            super().__init__(
                event_name="custom.research.created",
                aggregate_id=aggregate_id,
            )
            self._topic = topic

        def to_primitives(self):
            base = super().to_primitives()
            base["topic"] = self._topic
            return base

    custom_evt = CustomResearchEvent(aggregate_id="agg_abc", topic="Quantum Computing")
    assert isinstance(custom_evt, DomainEvent)
    assert custom_evt.event_name() == "custom.research.created"
    assert custom_evt.aggregate_id() == "agg_abc"
    prims = custom_evt.to_primitives()
    assert prims["topic"] == "Quantum Computing"
    assert prims["event_name"] == "custom.research.created"


def test_domain_event_meta():
    meta = DomainEventMeta(event_name="research.failed")
    assert meta.event_name == "research.failed"
    assert meta.EventName == "research.failed"
    assert meta.eventName == "research.failed"
    assert meta.to_dict() == {"event_name": "research.failed"}
    assert meta.to_primitives() == {"event_name": "research.failed"}

    meta2 = DomainEventMeta.from_dict({"eventName": "research.succeeded"})
    assert meta2.event_name == "research.succeeded"

