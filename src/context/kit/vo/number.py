import math
from typing import Union
from context.kit.vo.value_object import ValueObject


class Number(ValueObject):
    """
    Number Value Object.
    Traducción de Number struct de Go a Python.
    """

    def __init__(self, value: Union[int, float]) -> None:
        self._value: float = float(value)

    @classmethod
    def new(cls, value: Union[int, float]) -> "Number":
        return cls(value)

    def value(self) -> float:
        """Getter del valor numérico."""
        return self._value

    def Value(self) -> float:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def is_bigger_than(self, other: "Number") -> bool:
        """Compara si este valor es mayor que otro."""
        return self._value > other._value

    def IsBiggerThan(self, other: "Number") -> bool:
        """Alias para compatibilidad con Go (IsBiggerThan)."""
        return self.is_bigger_than(other)

    def format_to_two_decimal(self) -> None:
        """Redondea el valor interno a 2 decimales."""
        self._value = round(self._value, 2)

    def FormatToTwoDecimal(self) -> None:
        """Alias para compatibilidad con Go (FormatToTwoDecimal)."""
        self.format_to_two_decimal()

    def format_to_four_decimal(self) -> None:
        """Redondea el valor interno a 4 decimales."""
        self._value = round(self._value, 4)

    def FormatToFourDecimal(self) -> None:
        """Alias para compatibilidad con Go (FormatToFourDecimal)."""
        self.format_to_four_decimal()

    def format_to_six_decimal(self) -> None:
        """Redondea el valor interno a 6 decimales."""
        self._value = round(self._value, 6)

    def FormatToSixDecimal(self) -> None:
        """Alias para compatibilidad con Go (FormatToSixDecimal)."""
        self.format_to_six_decimal()

    def equals(self, other: "Number") -> bool:
        if not isinstance(other, Number):
            return False
        return math.isclose(self._value, other._value)

    def Equals(self, other: "Number") -> bool:
        return self.equals(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Number):
            return self._value == other._value
        if isinstance(other, (int, float)):
            return self._value == float(other)
        return False

    def __str__(self) -> str:
        if self._value.is_integer():
            return str(int(self._value))
        return str(self._value)

    def __repr__(self) -> str:
        return f"Number({self._value})"


def new_number(value: Union[int, float]) -> Number:
    """Constructor helper NewNumber."""
    return Number(value)


def NewNumber(value: Union[int, float]) -> Number:
    """Alias Go-style para new_number."""
    return new_number(value)

