from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LoggerService(ABC):
    """
    LoggerService define el contrato para el registro estructurado de eventos.
    Traducción de LoggerService interface de Go a Python.
    """

    @abstractmethod
    def info(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra mensajes informativos."""
        pass

    def Info(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Alias para compatibilidad con Go (Info)."""
        self.info(message, details)

    @abstractmethod
    def warn(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra advertencias."""
        pass

    def Warn(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Alias para compatibilidad con Go (Warn)."""
        self.warn(message, details)

    @abstractmethod
    def debug(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra mensajes de depuración."""
        pass

    def Debug(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Alias para compatibilidad con Go (Debug)."""
        self.debug(message, details)

    @abstractmethod
    def error(
        self,
        message: str,
        err: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra errores críticos."""
        pass

    def Error(
        self,
        message: str,
        err: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Alias para compatibilidad con Go (Error)."""
        self.error(message, err, details)

