import json
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.domain_event import BaseDomainEvent
from context.kit.dtos.domain_event_serializer import (
    DomainEventSerializer,
    SerializeDomainEvent,
    serialize_domain_event,
)


def test_serialize_domain_event():
    fixed_time = datetime(2026, 8, 24, 12, 30, 0, tzinfo=timezone.utc)
    event = BaseDomainEvent(
        event_name="research.started",
        aggregate_id="job_123",
        event_id="evt_abc",
        occurred_on=fixed_time,
    )

    json_str = SerializeDomainEvent(event)
    data = json.loads(json_str)

    assert "data" in data
    assert data["data"] == {
        "id": "evt_abc",
        "type": "research.started",
        "occurredOn": fixed_time.isoformat(),
        "aggregateId": "job_123",
        "attributes": {
            "event_name": "research.started",
            "aggregate_id": "job_123",
            "event_id": "evt_abc",
            "occurred_on": fixed_time.isoformat(),
        },
    }

    # Test serializer helper
    json_str_2 = serialize_domain_event(event)
    assert json_str_2 == json_str

    json_str_3 = DomainEventSerializer.serialize(event)
    assert json_str_3 == json_str


def test_deserialize_domain_event():
    raw_json = json.dumps(
        {
            "data": {
                "id": "evt_999",
                "type": "topic.analyzed",
                "occurredOn": "2026-08-24T12:00:00+00:00",
                "aggregateId": "agg_999",
                "attributes": {"score": 95},
            }
        }
    )

    parsed = DomainEventSerializer.deserialize(raw_json)
    assert parsed["data"]["id"] == "evt_999"
    assert parsed["data"]["type"] == "topic.analyzed"
    assert parsed["data"]["attributes"]["score"] == 95

