import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.aggregate_root import AggregateRoot
from context.kit.entity import BaseEntity, NewBaseEntity, new_base_entity
from context.kit.vo.uuid import RandomUuid
from context.kit.dtos.domain_event import NewBaseDomainEvent


def test_aggregate_root_record_and_pull():
    agg = AggregateRoot()
    assert len(agg.pull_domain_events()) == 0

    evt1 = NewBaseDomainEvent("order.created", "order_1")
    evt2 = NewBaseDomainEvent("order.paid", "order_1")

    agg.Record(evt1)
    agg.record(evt2)

    assert len(agg.get_domain_events()) == 2

    pulled = agg.PullDomainEvents()
    assert len(pulled) == 2
    assert pulled[0].event_name() == "order.created"
    assert pulled[1].event_name() == "order.paid"

    # Verificar que quedó limpio
    assert len(agg.pull_domain_events()) == 0


def test_base_entity():
    uid = RandomUuid()
    entity = NewBaseEntity(uid)

    assert entity.id == uid
    assert entity.ID == uid

    evt = NewBaseDomainEvent("entity.updated", uid.value())
    entity.Record(evt)

    assert len(entity.PullDomainEvents()) == 1

    entity2 = new_base_entity(uid.value())
    assert entity == entity2

