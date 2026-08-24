from context.kit.vo.value_object import ValueObject


class OrderBy(ValueObject):
    """
    OrderBy representa el campo por el cual se va a ordenar.
    """

    def __init__(self, value: str) -> None:
        self._value = str(value)

    def value(self) -> str:
        return self._value

    def Value(self) -> str:
        return self.value()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrderBy):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"OrderBy({self._value!r})"


def new_order_by(value: str) -> OrderBy:
    return OrderBy(value)


def NewOrderBy(value: str) -> OrderBy:
    return new_order_by(value)

