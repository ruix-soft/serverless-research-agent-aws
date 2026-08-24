from typing import Dict, Any, Optional


class DomainError(Exception):
    """
    DomainError clase base para errores de dominio.
    Traducción de DomainError struct de Go a Python.
    """

    def __init__(
        self,
        err_type: str,
        message: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self._err_type = err_type
        self._message = message
        self._attributes = attributes if attributes is not None else {}

    @property
    def message(self) -> str:
        """Mensaje descriptivo del error."""
        return self._message

    def Message(self) -> str:
        """Alias para compatibilidad con Go (Message)."""
        return self.message

    @property
    def err_type(self) -> str:
        """Identificador único del tipo de error (p.ej. 'user_not_found')."""
        return self._err_type

    @property
    def type(self) -> str:
        """Alias de err_type."""
        return self._err_type

    def Type(self) -> str:
        """Alias para compatibilidad con Go (Type)."""
        return self.err_type

    @property
    def attributes(self) -> Dict[str, Any]:
        """Atributos adicionales del error."""
        return self._attributes

    @property
    def code(self) -> str:
        """Alias para err_type / tipo de error."""
        return self._err_type

    @property
    def details(self) -> Dict[str, Any]:
        """Alias para attributes."""
        return self._attributes

    def Attributes(self) -> Dict[str, Any]:
        """Alias para compatibilidad con Go (Attributes)."""
        return self.attributes

    def error(self) -> str:
        """Implementación del mensaje de error."""
        return self._message

    def Error(self) -> str:
        """Alias para compatibilidad con Go (Error)."""
        return self.error()

    def to_primitives(self) -> Dict[str, Any]:
        """
        Convierte el error a una representación serializable (JSON friendly).
        Retorna la estructura {'type': ..., 'message': ..., 'data': ...}.
        """
        return {
            "type": self._err_type,
            "message": self._message,
            "data": self._attributes,
        }

    def ToPrimitives(self) -> Dict[str, Any]:
        """Alias para compatibilidad con Go (ToPrimitives)."""
        return self.to_primitives()

    def to_dict(self) -> Dict[str, Any]:
        """Alias para to_primitives."""
        return self.to_primitives()

    @classmethod
    def from_primitives(cls, data: Dict[str, Any]) -> "DomainError":
        """Rehidrata un DomainError desde un diccionario de primitivos."""
        err_type = data.get("type") or data.get("err_type") or data.get("errType") or "DOMAIN_ERROR"
        message = data.get("message") or ""
        attributes = data.get("data") or data.get("attributes") or {}
        return cls(err_type=err_type, message=message, attributes=attributes)

    def __str__(self) -> str:
        return self._message

    def __repr__(self) -> str:
        return (
            f"DomainError(err_type={self._err_type!r}, "
            f"message={self._message!r}, "
            f"attributes={self._attributes!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainError):
            return False
        return (
            self._err_type == other._err_type
            and self._message == other._message
            and self._attributes == other._attributes
        )


# --- CONSTRUCTOR HELPER (traducción directa de Go) ---


def new_domain_error(
    err_type: str,
    message: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> DomainError:
    """
    Constructor helper.
    Equivalente a NewDomainError(errType string, message string, attributes map[string]interface{}).
    """
    return DomainError(err_type=err_type, message=message, attributes=attributes)


def NewDomainError(
    err_type: str,
    message: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> DomainError:
    """Alias Go-style para new_domain_error."""
    return new_domain_error(err_type=err_type, message=message, attributes=attributes)

