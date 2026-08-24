from context.kit.vo.value_object import ValueObject


class String(ValueObject):
    """
    String Value Object base para cadenas de texto.
    Traducción de String struct de Go a Python.
    """

    def __init__(self, value: str) -> None:
        self._value: str = str(value)

    @classmethod
    def new(cls, value: str) -> "String":
        return cls(value)

    def value(self) -> str:
        """Getter para obtener el valor primitivo."""
        return self._value

    def Value(self) -> str:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def clean(self) -> None:
        """Limpia el string (trim de espacios en blanco)."""
        self._value = self._value.strip()

    def Clean(self) -> None:
        """Alias para compatibilidad con Go (Clean)."""
        self.clean()

    def set_first_characters(self, count: int) -> None:
        """Actualiza el valor interno con los primeros N caracteres (mutación)."""
        self._value = self.get_first_characters(count)

    def SetFirstCharacters(self, count: int) -> None:
        """Alias para compatibilidad con Go (SetFirstCharacters)."""
        self.set_first_characters(count)

    def get_first_characters(self, count: int) -> str:
        """
        Retorna los primeros N caracteres respetando caracteres unicode/emojis.
        No modifica el estado interno.
        """
        if count < 0:
            return self._value
        if count > len(self._value):
            return self._value
        return self._value[:count]

    def GetFirstCharacters(self, count: int) -> str:
        """Alias para compatibilidad con Go (GetFirstCharacters)."""
        return self.get_first_characters(count)

    def equals(self, other: "String") -> bool:
        if not isinstance(other, String):
            return False
        return self._value == other._value

    def Equals(self, other: "String") -> bool:
        return self.equals(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, String):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"String({self._value!r})"


def new_string(value: str) -> String:
    """Constructor helper NewString."""
    return String(value)


def NewString(value: str) -> String:
    """Alias Go-style para new_string."""
    return new_string(value)

