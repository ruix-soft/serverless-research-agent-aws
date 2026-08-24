from typing import Union
from context.kit.vo.value_object import ValueObject


class Boolean(ValueObject):
    """
    Boolean Value Object.
    Traducción de Boolean struct de Go a Python.
    """

    def __init__(self, value: bool) -> None:
        self._value = bool(value)

    @classmethod
    def new(cls, value: bool) -> "Boolean":
        return cls(value)

    def value(self) -> bool:
        """Retorna el valor primitivo booleano."""
        return self._value

    def Value(self) -> bool:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def is_true(self) -> bool:
        """Helper semántico para verificar si es True."""
        return self._value is True

    def IsTrue(self) -> bool:
        """Alias para compatibilidad con Go (IsTrue)."""
        return self.is_true()

    def is_false(self) -> bool:
        """Helper semántico para verificar si es False."""
        return self._value is False

    def IsFalse(self) -> bool:
        """Alias para compatibilidad con Go (IsFalse)."""
        return self.is_false()

    def negate(self) -> None:
        """Invierte el valor actual (mutación interna)."""
        self._value = not self._value

    def Negate(self) -> None:
        """Alias para compatibilidad con Go (Negate)."""
        self.negate()

    def equals(self, other: "Boolean") -> bool:
        """Compara si dos Value Objects son iguales."""
        if not isinstance(other, Boolean):
            return False
        return self._value == other._value

    def Equals(self, other: "Boolean") -> bool:
        """Alias para compatibilidad con Go (Equals)."""
        return self.equals(other)

    def __bool__(self) -> bool:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Boolean):
            return self._value == other._value
        if isinstance(other, bool):
            return self._value == other
        return False

    def __str__(self) -> str:
        return "true" if self._value else "false"

    def __repr__(self) -> str:
        return f"Boolean({self._value})"


def new_boolean(value: bool) -> Boolean:
    """Constructor helper NewBoolean."""
    return Boolean(value)


def NewBoolean(value: bool) -> Boolean:
    """Alias Go-style para new_boolean."""
    return new_boolean(value)

