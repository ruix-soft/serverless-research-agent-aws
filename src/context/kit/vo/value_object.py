from abc import ABC, abstractmethod


class ValueObject(ABC):
    """
    ValueObject es una interfaz / clase base abstracta para marcar objetos de valor.
    Traducción de ValueObject interface de Go a Python.
    """

    @abstractmethod
    def __str__(self) -> str:
        pass

