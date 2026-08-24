"""
Kit package containing reusable foundational utilities, DTOs, CQRS building blocks, Value Objects, and error structures.
"""
from context.kit.aggregate_root import AggregateRoot
from context.kit.entity import BaseEntity, NewBaseEntity, new_base_entity

__all__ = [
    "AggregateRoot",
    "BaseEntity",
    "NewBaseEntity",
    "new_base_entity",
]
