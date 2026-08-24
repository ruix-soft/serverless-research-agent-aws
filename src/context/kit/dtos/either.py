from typing import Generic, TypeVar, Callable, Any, Optional, Union

L = TypeVar("L")
R = TypeVar("R")
T = TypeVar("T")


class Either(Generic[L, R]):
    """
    Either representa un valor que puede ser de dos tipos: L (Left) o R (Right).
    Traducción de Either[L any, R any] de Go a Python con soporte de tipos genéricos.
    """

    def __init__(
        self,
        left: Optional[L] = None,
        right: Optional[R] = None,
        is_left: bool = False,
    ) -> None:
        self._left: Optional[L] = left
        self._right: Optional[R] = right
        self._is_left: bool = is_left

    @classmethod
    def left(cls, value: L) -> "Either[L, R]":
        """Crea una instancia de Left."""
        return cls(left=value, right=None, is_left=True)

    @classmethod
    def Left(cls, value: L) -> "Either[L, R]":
        """Alias para compatibilidad (Left)."""
        return cls.left(value)

    @classmethod
    def new_left(cls, value: L) -> "Either[L, R]":
        """Crea una instancia de Left (equivalente a NewLeft)."""
        return cls.left(value)

    @classmethod
    def NewLeft(cls, value: L) -> "Either[L, R]":
        """Alias Go-style para NewLeft."""
        return cls.left(value)

    @classmethod
    def right(cls, value: R) -> "Either[L, R]":
        """Crea una instancia de Right."""
        return cls(left=None, right=value, is_left=False)

    @classmethod
    def Right(cls, value: R) -> "Either[L, R]":
        """Alias para compatibilidad (Right)."""
        return cls.right(value)

    @classmethod
    def new_right(cls, value: R) -> "Either[L, R]":
        """Crea una instancia de Right (equivalente a NewRight)."""
        return cls.right(value)

    @classmethod
    def NewRight(cls, value: R) -> "Either[L, R]":
        """Alias Go-style para NewRight."""
        return cls.right(value)

    def is_left(self) -> bool:
        """Verifica si es Left."""
        return self._is_left

    def IsLeft(self) -> bool:
        """Alias para compatibilidad con Go (IsLeft)."""
        return self.is_left()

    def is_right(self) -> bool:
        """Verifica si es Right."""
        return not self._is_left

    def IsRight(self) -> bool:
        """Alias para compatibilidad con Go (IsRight)."""
        return self.is_right()

    def get(self) -> R:
        """
        Obtiene el valor Right.
        Lanza ValueError si la instancia es Left.
        """
        if self._is_left:
            raise ValueError("cannot get right value from left Either")
        return self._right  # type: ignore

    def Get(self) -> R:
        """Alias para compatibilidad con Go (Get)."""
        return self.get()

    def get_left(self) -> L:
        """
        Obtiene el valor Left.
        Lanza ValueError si la instancia es Right.
        """
        if not self._is_left:
            raise ValueError("cannot get left value from right Either")
        return self._left  # type: ignore

    def GetLeft(self) -> L:
        """Alias para compatibilidad con Go (GetLeft)."""
        return self.get_left()

    def fold(self, left_fn: Callable[[L], T], right_fn: Callable[[R], T]) -> T:
        """
        Colapsa el Either a un solo tipo T ejecutando left_fn o right_fn.
        """
        if self._is_left:
            return left_fn(self.get_left())
        return right_fn(self.get())

    def Fold(self, left_fn: Callable[[L], T], right_fn: Callable[[R], T]) -> T:
        """Alias para compatibilidad con Go (Fold)."""
        return self.fold(left_fn, right_fn)

    def map(self, fn: Callable[[R], T]) -> "Either[L, T]":
        """
        Transforma el lado Right (R) a un nuevo tipo (T).
        Si es Left, se conserva el valor Left original.
        """
        if self._is_left:
            return Either.left(self.get_left())
        return Either.right(fn(self.get()))

    def Map(self, fn: Callable[[R], T]) -> "Either[L, T]":
        """Alias para compatibilidad con Go (Map)."""
        return self.map(fn)

    def __bool__(self) -> bool:
        return self.is_right()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Either):
            return False
        if self._is_left != other._is_left:
            return False
        if self._is_left:
            return self._left == other._left
        return self._right == other._right

    def __repr__(self) -> str:
        if self._is_left:
            return f"Either.left({self._left!r})"
        return f"Either.right({self._right!r})"


# --- FUNCIONES DE ALTO NIVEL (Helpers traducidos directamente de Go) ---


def new_left(value: L) -> Either[L, Any]:
    """
    Crea una instancia de Left.
    Equivalente a NewLeft[L, R](value).
    """
    return Either.left(value)


def NewLeft(value: L) -> Either[L, Any]:
    """Alias Go-style para new_left."""
    return Either.left(value)


def new_right(value: R) -> Either[Any, R]:
    """
    Crea una instancia de Right.
    Equivalente a NewRight[L, R](value).
    """
    return Either.right(value)


def NewRight(value: R) -> Either[Any, R]:
    """Alias Go-style para new_right."""
    return Either.right(value)


def fold(
    e: Either[L, R],
    left_fn: Callable[[L], T],
    right_fn: Callable[[R], T],
) -> T:
    """
    Colapsa el Either a un solo tipo T.
    Equivalente a Fold[L, R, T](e, leftFn, rightFn).
    """
    return e.fold(left_fn, right_fn)


def Fold(
    e: Either[L, R],
    left_fn: Callable[[L], T],
    right_fn: Callable[[R], T],
) -> T:
    """Alias Go-style para fold."""
    return e.fold(left_fn, right_fn)


def either_map(e: Either[L, R], fn: Callable[[R], T]) -> Either[L, T]:
    """
    Transforma el lado Right (R) a un nuevo tipo (T).
    Equivalente a Map[L, R, T](e, fn).
    """
    return e.map(fn)


def Map(e: Either[L, R], fn: Callable[[R], T]) -> Either[L, T]:
    """Alias Go-style para either_map."""
    return either_map(e, fn)

