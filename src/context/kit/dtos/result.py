from typing import Generic, TypeVar, Callable, Any, Union, Optional

O = TypeVar("O")
E = TypeVar("E")
T = TypeVar("T")


class Result(Generic[O, E]):
    """
    Representa el resultado de una operación que puede ser Exitosa (O) o Fallida (E).
    Traducción de Result[O any, E any] de Go a Python con soporte de tipos genéricos.
    """

    def __init__(
        self,
        value: Optional[O] = None,
        err: Optional[E] = None,
        is_err: bool = False,
    ) -> None:
        self._value: Optional[O] = value
        self._err: Optional[E] = err
        self._is_err: bool = is_err

    @classmethod
    def ok(cls, value: O) -> "Result[O, E]":
        """
        Crea un Result exitoso.
        Equivalente a Result.ok(value) / Ok(value).
        """
        return cls(value=value, err=None, is_err=False)

    @classmethod
    def Ok(cls, value: O) -> "Result[O, E]":
        """Alias para compatibilidad con Go (Ok / Result.Ok)."""
        return cls.ok(value)

    @classmethod
    def err(cls, err: E) -> "Result[O, E]":
        """
        Crea un Result fallido.
        Equivalente a Result.error(err) / Err(err).
        """
        return cls(value=None, err=err, is_err=True)

    @classmethod
    def Err(cls, err: E) -> "Result[O, E]":
        """Alias para compatibilidad con Go (Err / Result.Err)."""
        return cls.err(err)

    @classmethod
    def fail(cls, err: E) -> "Result[O, E]":
        """Alias pythonic/TS para crear un Result fallido."""
        return cls.err(err)

    @classmethod
    def Fail(cls, err: E) -> "Result[O, E]":
        """Alias para crear un Result fallido."""
        return cls.err(err)

    def is_ok(self) -> bool:
        """Verifica si es exitoso."""
        return not self._is_err

    def IsOk(self) -> bool:
        """Alias para compatibilidad con Go (IsOk)."""
        return not self._is_err

    def is_error(self) -> bool:
        """Verifica si es fallido."""
        return self._is_err

    def IsError(self) -> bool:
        """Alias para compatibilidad con Go (IsError)."""
        return self._is_err

    def is_err(self) -> bool:
        """Alias para is_error."""
        return self._is_err

    def get(self) -> O:
        """
        Obtiene el valor exitoso.
        Lanza ValueError si el Result es un error.
        """
        if self._is_err:
            raise ValueError(f"cannot get ok value from error result: {self._err}")
        return self._value  # type: ignore

    def Get(self) -> O:
        """Alias para compatibilidad con Go (Get)."""
        return self.get()

    def get_error(self) -> E:
        """
        Obtiene el error.
        Lanza ValueError si el Result es un éxito.
        """
        if not self._is_err:
            raise ValueError("cannot get error value from ok result")
        return self._err  # type: ignore

    def GetError(self) -> E:
        """Alias para compatibilidad con Go (GetError)."""
        return self.get_error()

    @property
    def value(self) -> O:
        """Propiedad para obtener el valor exitoso."""
        return self.get()

    @property
    def error(self) -> E:
        """Propiedad para obtener el error."""
        return self.get_error()

    def map(self, fn: Callable[[O], T]) -> "Result[T, E]":
        """
        Transforma el valor Ok si existe usando la función fn.
        """
        if self._is_err:
            return Result.err(self._err)  # type: ignore
        return Result.ok(fn(self.get()))

    def Map(self, fn: Callable[[O], T]) -> "Result[T, E]":
        """Alias para compatibilidad con Go (Map)."""
        return self.map(fn)

    def fold(self, ok_fn: Callable[[O], T], error_fn: Callable[[E], T]) -> T:
        """
        Desempaqueta el resultado ejecutando una de las dos funciones.
        """
        if self._is_err:
            return error_fn(self.get_error())
        return ok_fn(self.get())

    def Fold(self, ok_fn: Callable[[O], T], error_fn: Callable[[E], T]) -> T:
        """Alias para compatibilidad con Go (Fold)."""
        return self.fold(ok_fn, error_fn)

    def __bool__(self) -> bool:
        return self.is_ok()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False
        if self._is_err != other._is_err:
            return False
        if self._is_err:
            return self._err == other._err
        return self._value == other._value

    def __repr__(self) -> str:
        if self.is_ok():
            return f"Result.ok({self._value!r})"
        return f"Result.err({self._err!r})"


# --- FUNCIONES DE ALTO NIVEL (Helpers traducidos directamente de Go) ---


def ok(value: O) -> Result[O, Any]:
    """
    Crea un Result exitoso.
    Equivalente a Ok[O, E](value).
    """
    return Result.ok(value)


def Ok(value: O) -> Result[O, Any]:
    """Alias Go-style para ok."""
    return Result.ok(value)


def err(error: E) -> Result[Any, E]:
    """
    Crea un Result fallido.
    Equivalente a Err[O, E](err).
    """
    return Result.err(error)


def Err(error: E) -> Result[Any, E]:
    """Alias Go-style para err."""
    return Result.err(error)


def result_map(r: Result[O, E], fn: Callable[[O], T]) -> Result[T, E]:
    """
    Transforma el valor Ok si existe.
    Equivalente a ResultMap[O, E, T](r, fn).
    """
    if r.is_error():
        return Result.err(r.get_error())
    return Result.ok(fn(r.get()))


def ResultMap(r: Result[O, E], fn: Callable[[O], T]) -> Result[T, E]:
    """Alias Go-style para result_map."""
    return result_map(r, fn)


def result_fold(
    r: Result[O, E],
    ok_fn: Callable[[O], T],
    error_fn: Callable[[E], T],
) -> T:
    """
    Desempaqueta el resultado ejecutando una de las dos funciones.
    Equivalente a ResultFold[O, E, T](r, okFn, errorFn).
    """
    if r.is_error():
        return error_fn(r.get_error())
    return ok_fn(r.get())


def ResultFold(
    r: Result[O, E],
    ok_fn: Callable[[O], T],
    error_fn: Callable[[E], T],
) -> T:
    """Alias Go-style para result_fold."""
    return result_fold(r, ok_fn, error_fn)
