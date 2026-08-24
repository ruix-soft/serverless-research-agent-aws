from typing import Generic, TypeVar, Callable, Any, Union

T = TypeVar("T")
R = TypeVar("R")


class Optional(Generic[T]):
    """
    Representa un contenedor que puede o no contener un valor no nulo.
    Traducción de Optional[T any] de Go a Python con soporte de tipos genéricos.
    """

    def __init__(self, value: Any = None, present: bool = False) -> None:
        self._value: T = value
        self._present: bool = present

    @classmethod
    def of(cls, value: T) -> "Optional[T]":
        """
        Crea un Optional con un valor presente.
        Equivalente a Optional.of(value) / OptionalOf(value).
        """
        return cls(value=value, present=True)

    @classmethod
    def Of(cls, value: T) -> "Optional[T]":
        """Alias para compatibilidad con Go (OptionalOf / Optional.Of)."""
        return cls.of(value)

    @classmethod
    def empty(cls) -> "Optional[T]":
        """
        Crea una instancia de Optional vacía.
        Equivalente a Optional.empty() / OptionalEmpty().
        """
        return cls(value=None, present=False)

    @classmethod
    def Empty(cls) -> "Optional[T]":
        """Alias para compatibilidad con Go (OptionalEmpty / Optional.Empty)."""
        return cls.empty()

    def is_present(self) -> bool:
        """Devuelve True si hay un valor presente."""
        return self._present

    def IsPresent(self) -> bool:
        """Alias para compatibilidad con Go (IsPresent)."""
        return self.is_present()

    def is_empty(self) -> bool:
        """Devuelve True si no hay valor presente."""
        return not self._present

    def IsEmpty(self) -> bool:
        """Alias para compatibilidad con Go (IsEmpty)."""
        return self.is_empty()

    def get(self) -> T:
        """
        Devuelve el valor.
        Lanza ValueError si el Optional está vacío.
        """
        if not self._present:
            raise ValueError("Cannot get value from an empty Optional.")
        return self._value

    def Get(self) -> T:
        """Alias para compatibilidad con Go (Get)."""
        return self.get()

    def or_else(self, other: T) -> T:
        """
        Devuelve el valor si está presente, o el valor 'other' si no lo está.
        """
        if self._present:
            return self._value
        return other

    def OrElse(self, other: T) -> T:
        """Alias para compatibilidad con Go (OrElse)."""
        return self.or_else(other)

    def or_else_throw(
        self,
        error: Union[Exception, type[Exception], Callable[[], Exception], None] = None,
    ) -> T:
        """
        Devuelve el valor si está presente o lanza la excepción indicada si está vacío.
        Si no se provee error, lanza ValueError por defecto.
        """
        if self._present:
            return self._value

        if error is None:
            raise ValueError("Value is not present in Optional.")

        if isinstance(error, type) and issubclass(error, BaseException):
            raise error()

        if isinstance(error, BaseException):
            raise error

        if callable(error):
            err_instance = error()
            if isinstance(err_instance, BaseException):
                raise err_instance
            raise ValueError(str(err_instance))

        raise ValueError(str(error))

    def OrElseThrow(
        self,
        error: Union[Exception, type[Exception], Callable[[], Exception], None] = None,
    ) -> T:
        """Alias para compatibilidad con Go (OrElseThrow)."""
        return self.or_else_throw(error)

    def or_else_get(self, supplier: Callable[[], T]) -> T:
        """
        Devuelve el valor si está presente, o el resultado del callable supplier si no.
        """
        if self._present:
            return self._value
        return supplier()

    def OrElseGet(self, supplier: Callable[[], T]) -> T:
        """Alias camelCase para or_else_get."""
        return self.or_else_get(supplier)

    def map(self, mapper: Callable[[T], R]) -> "Optional[R]":
        """
        Transforma el valor dentro del Optional si está presente usando la función mapper.
        """
        if not self._present:
            return Optional.empty()
        return Optional.of(mapper(self._value))

    def Map(self, mapper: Callable[[T], R]) -> "Optional[R]":
        """Alias para compatibilidad con Go (Map)."""
        return self.map(mapper)

    def __bool__(self) -> bool:
        return self._present

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Optional):
            return False
        if self._present != other._present:
            return False
        if not self._present:
            return True
        return self._value == other._value

    def __repr__(self) -> str:
        if self._present:
            return f"Optional.of({self._value!r})"
        return "Optional.empty()"


# --- FUNCIONES DE ALTO NIVEL (Helpers traducidos directamente de Go) ---


def optional_of(value: T) -> Optional[T]:
    """
    Crea un Optional con un valor presente.
    Equivalente a OptionalOf[T](value).
    """
    return Optional.of(value)


def OptionalOf(value: T) -> Optional[T]:
    """Alias Go-style para optional_of."""
    return Optional.of(value)


def optional_empty() -> Optional[Any]:
    """
    Crea una instancia de Optional vacía.
    Equivalente a OptionalEmpty[T]().
    """
    return Optional.empty()


def OptionalEmpty() -> Optional[Any]:
    """Alias Go-style para optional_empty."""
    return Optional.empty()


def optional_map(o: Optional[T], mapper: Callable[[T], R]) -> Optional[R]:
    """
    Transforma el valor dentro del Optional si está presente.
    Equivalente a OptionalMap[T, R](o, mapper).
    """
    if not o.is_present():
        return Optional.empty()
    return Optional.of(mapper(o.get()))


def OptionalMap(o: Optional[T], mapper: Callable[[T], R]) -> Optional[R]:
    """Alias Go-style para optional_map."""
    return optional_map(o, mapper)

