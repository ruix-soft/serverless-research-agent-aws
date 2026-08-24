import uuid
from typing import Union
from context.kit.vo.value_object import ValueObject


class Uuid(ValueObject):
    """
    Uuid Value Object con validación y generación segura.
    Traducción de Uuid struct de Go a Python.
    """

    def __init__(self, value: str) -> None:
        val_str = str(value)
        if not self._validate(val_str):
            raise ValueError(f"<Uuid> does not allow the value <{val_str}>")
        self._value = val_str

    @classmethod
    def create(cls, value: str) -> "Uuid":
        return cls(value)

    @classmethod
    def random(cls) -> "Uuid":
        """Genera un nuevo UUID aleatorio v4."""
        return cls(str(uuid.uuid4()))

    @classmethod
    def RandomUuid(cls) -> "Uuid":
        """Alias Go-style para random."""
        return cls.random()

    @staticmethod
    def _validate(id_str: str) -> bool:
        try:
            val = uuid.UUID(id_str)
            return str(val) == id_str.lower()
        except (ValueError, AttributeError, TypeError):
            return False

    def value(self) -> str:
        """Getter del valor primitivo."""
        return self._value

    def Value(self) -> str:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def equals(self, other: "Uuid") -> bool:
        if not isinstance(other, Uuid):
            return False
        return self._value.lower() == other._value.lower()

    def Equals(self, other: "Uuid") -> bool:
        return self.equals(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Uuid):
            return self._value.lower() == other._value.lower()
        if isinstance(other, str):
            return self._value.lower() == other.lower()
        return False

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Uuid({self._value!r})"


def new_uuid(value: str) -> Uuid:
    """Constructor helper NewUuid."""
    return Uuid(value)


def NewUuid(value: str) -> Uuid:
    """Alias Go-style para new_uuid."""
    return new_uuid(value)


def random_uuid() -> Uuid:
    """Generador aleatorio RandomUuid."""
    return Uuid.random()


def RandomUuid() -> Uuid:
    """Alias Go-style para random_uuid."""
    return random_uuid()

