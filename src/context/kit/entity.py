from typing import Optional, Union
from context.kit.aggregate_root import AggregateRoot
from context.kit.vo.uuid import Uuid, new_uuid


class BaseEntity(AggregateRoot):
    """
    BaseEntity combina AggregateRoot y un ID único basado en Uuid.
    Traducción de BaseEntity struct de Go a Python.
    """

    def __init__(self, id: Union[Uuid, str]) -> None:
        super().__init__()
        if isinstance(id, str):
            self._id = new_uuid(id)
        else:
            self._id = id

    @property
    def id(self) -> Uuid:
        """Retorna el Value Object Uuid de la entidad."""
        return self._id

    @property
    def ID(self) -> Uuid:
        """Alias para compatibilidad con Go (ID)."""
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other._id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r})"


def new_base_entity(id: Union[Uuid, str]) -> BaseEntity:
    """Constructor helper NewBaseEntity."""
    return BaseEntity(id)


def NewBaseEntity(id: Union[Uuid, str]) -> BaseEntity:
    """Alias Go-style para new_base_entity."""
    return new_base_entity(id)

