from context.kit.vo.value_object import ValueObject


class FilterField(ValueObject):
    """
    FilterField representa el nombre del campo por el cual se va a filtrar.
    Traducción de FilterField de Go a Python.
    """

    def __init__(self, value: str) -> None:
        self._value = str(value)

    def value(self) -> str:
        """Retorna el valor primitivo (string)."""
        return self._value

    def Value(self) -> str:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FilterField):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"FilterField({self._value!r})"


def new_filter_field(value: str) -> FilterField:
    return FilterField(value)


def NewFilterField(value: str) -> FilterField:
    return new_filter_field(value)

