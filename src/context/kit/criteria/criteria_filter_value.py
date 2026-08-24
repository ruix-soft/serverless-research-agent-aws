from typing import Any
from context.kit.vo.value_object import ValueObject


class FilterValue(ValueObject):
    """
    FilterValue representa el valor contra el cual se compara en un filtro.
    """

    def __init__(self, value: Any) -> None:
        self._value = value

    def value(self) -> Any:
        return self._value

    def Value(self) -> Any:
        return self.value()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FilterValue):
            return self._value == other._value
        return self._value == other

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"FilterValue({self._value!r})"


def new_filter_value(value: Any) -> FilterValue:
    return FilterValue(value)


def NewFilterValue(value: Any) -> FilterValue:
    return new_filter_value(value)

