from typing import Any, Union
from context.kit.criteria.criteria_filter_field import FilterField, new_filter_field
from context.kit.criteria.criteria_filter_operator import FilterOperator, new_filter_operator
from context.kit.criteria.criteria_filter_value import FilterValue, new_filter_value


class Filter:
    """
    Filter agrupa un campo, un operador y un valor para definir una condición de búsqueda.
    """

    def __init__(self, field: FilterField, operator: FilterOperator, value: FilterValue) -> None:
        self._field = field
        self._operator = operator
        self._value = value

    @classmethod
    def from_primitives(cls, field: str, operator: Union[str, FilterOperator], value: Any) -> "Filter":
        """
        Crea un Filter a partir de valores primitivos con validación.
        """
        if not field:
            raise ValueError("the field is required")

        op = operator if isinstance(operator, FilterOperator) else new_filter_operator(operator)
        val = new_filter_value(value)
        f_field = new_filter_field(field)

        return cls(f_field, op, val)

    def field(self) -> FilterField:
        return self._field

    def Field(self) -> FilterField:
        return self.field()

    def operator(self) -> FilterOperator:
        return self._operator

    def Operator(self) -> FilterOperator:
        return self.operator()

    def value(self) -> FilterValue:
        return self._value

    def Value(self) -> FilterValue:
        return self.value()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filter):
            return False
        return (
            self._field == other._field
            and self._operator == other._operator
            and self._value == other._value
        )

    def __repr__(self) -> str:
        return f"Filter(field={self._field!r}, operator={self._operator!r}, value={self._value!r})"


def new_filter(field: FilterField, operator: FilterOperator, value: FilterValue) -> Filter:
    return Filter(field, operator, value)


def NewFilter(field: FilterField, operator: FilterOperator, value: FilterValue) -> Filter:
    return new_filter(field, operator, value)


def new_filter_from_primitives(field: str, operator: Union[str, FilterOperator], value: Any) -> Filter:
    return Filter.from_primitives(field, operator, value)


def NewFilterFromPrimitives(field: str, operator: Union[str, FilterOperator], value: Any) -> Filter:
    return new_filter_from_primitives(field, operator, value)

