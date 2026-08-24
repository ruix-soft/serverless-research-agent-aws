from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class Metadata:
    """
    Metadata contiene información común de auditoría y rastreo.
    Traducción de Metadata struct de Go a Python.
    """

    user: str
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    timestamp: Optional[datetime] = None
    correlation_id: Optional[str] = None

    @property
    def User(self) -> str:
        """Alias para compatibilidad con Go (User)."""
        return self.user

    @property
    def UserAgent(self) -> Optional[str]:
        """Alias para compatibilidad con Go (UserAgent)."""
        return self.user_agent

    @property
    def IP(self) -> Optional[str]:
        """Alias para compatibilidad con Go (IP)."""
        return self.ip

    @property
    def Timestamp(self) -> Optional[datetime]:
        """Alias para compatibilidad con Go (Timestamp)."""
        return self.timestamp

    @property
    def CorrelationID(self) -> Optional[str]:
        """Alias para compatibilidad con Go (CorrelationID)."""
        return self.correlation_id

    @property
    def userAgent(self) -> Optional[str]:
        """Alias camelCase para user_agent."""
        return self.user_agent

    @property
    def correlationId(self) -> Optional[str]:
        """Alias camelCase para correlation_id."""
        return self.correlation_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa Metadata a un diccionario omitiendo campos nulos/vacíos (omitempty).
        """
        data: Dict[str, Any] = {"user": self.user}

        if self.user_agent:
            data["userAgent"] = self.user_agent

        if self.ip:
            data["ip"] = self.ip

        if self.timestamp:
            data["timestamp"] = self.timestamp.isoformat()

        if self.correlation_id:
            data["correlationId"] = self.correlation_id

        return data

    def to_primitives(self) -> Dict[str, Any]:
        """Alias para to_dict cumpliendo convenciones DDD del proyecto."""
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metadata":
        """
        Deserializa un diccionario a una instancia de Metadata.
        Soporta claves tanto en camelCase como en snake_case.
        """
        user = data.get("user") or data.get("User") or ""
        user_agent = data.get("userAgent") or data.get("user_agent") or data.get("UserAgent")
        ip = data.get("ip") or data.get("IP")
        correlation_id = (
            data.get("correlationId")
            or data.get("correlation_id")
            or data.get("CorrelationID")
        )

        raw_ts = data.get("timestamp") or data.get("Timestamp")
        timestamp: Optional[datetime] = None
        if isinstance(raw_ts, datetime):
            timestamp = raw_ts
        elif isinstance(raw_ts, str) and raw_ts:
            try:
                timestamp = datetime.fromisoformat(raw_ts)
            except ValueError:
                timestamp = None

        return cls(
            user=user,
            user_agent=user_agent,
            ip=ip,
            timestamp=timestamp,
            correlation_id=correlation_id,
        )

    @classmethod
    def from_primitives(cls, data: Dict[str, Any]) -> "Metadata":
        """Alias para from_dict cumpliendo convenciones DDD del proyecto."""
        return cls.from_dict(data)


# --- CONSTRUCTORES HELPER (traducción directa de Go) ---


def new_metadata(user: str, correlation_id: Optional[str] = None) -> Metadata:
    """
    Constructor helper opcional.
    Facilita la creación con el timestamp actual en UTC por defecto.
    Equivalente a NewMetadata(user string, correlationID string).
    """
    return Metadata(
        user=user,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc),
    )


def NewMetadata(user: str, correlation_id: Optional[str] = None) -> Metadata:
    """Alias Go-style para new_metadata."""
    return new_metadata(user=user, correlation_id=correlation_id)

