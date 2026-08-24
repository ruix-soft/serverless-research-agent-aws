import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Union
from context.kit.vo.value_object import ValueObject


class Date(ValueObject):
    """
    Date Value Object con soporte para ISO 8601, formateos estándar y cálculo de días.
    Traducción de Date struct de Go a Python.
    """

    def __init__(self, value: Optional[datetime] = None) -> None:
        if value is None:
            self._value = datetime.now(timezone.utc)
        else:
            self._value = value

    @classmethod
    def now(cls) -> "Date":
        return cls(datetime.now(timezone.utc))

    @classmethod
    def NewDateNow(cls) -> "Date":
        return cls.now()

    def value(self) -> datetime:
        """Getter del objeto datetime subyacente."""
        return self._value

    def Value(self) -> datetime:
        """Alias para compatibilidad con Go (Value)."""
        return self.value()

    def add_days(self, days: int) -> "Date":
        """
        Retorna una NUEVA instancia con los días añadidos (Inmutable).
        """
        new_dt = self._value + timedelta(days=days)
        return Date(new_dt)

    def AddDays(self, days: int) -> "Date":
        """Alias para compatibilidad con Go (AddDays)."""
        return self.add_days(days)

    def to_ymd_his_string(self) -> str:
        """Formato YYYY-MM-DD HH:mm:ss."""
        return self._value.strftime("%Y-%m-%d %H:%M:%S")

    def ToYmdHisString(self) -> str:
        """Alias Go-style para to_ymd_his_string."""
        return self.to_ymd_his_string()

    def to_ymd_his_with_dot_string(self) -> str:
        """Alias para compatibilidad."""
        return self.to_ymd_his_string()

    def ToYmdHisWithDotString(self) -> str:
        return self.to_ymd_his_string()

    def to_ymd_string(self) -> str:
        """Formato YYYY-MM-DD."""
        return self._value.strftime("%Y-%m-%d")

    def ToYmdString(self) -> str:
        """Alias Go-style para to_ymd_string."""
        return self.to_ymd_string()

    def to_ymd_no_hyphens_string(self) -> str:
        """Formato YYYYMMDD."""
        return self._value.strftime("%Y%m%d")

    def ToYmdNoHyphensString(self) -> str:
        """Alias Go-style para to_ymd_no_hyphens_string."""
        return self.to_ymd_no_hyphens_string()

    @classmethod
    def from_standard_string(cls, standard: str) -> "Date":
        """
        Parsea strings de fecha estándar ("YYYY-MM-DD HH:mm:ss", "YYYY-MM-DDTHH:mm:ss", etc.).
        """
        if not standard:
            raise ValueError("Standard date string cannot be empty")

        # Separar fecha y hora por espacio o 'T'
        parts = re.split(r"[ T]", standard)
        if len(parts) < 2:
            raise ValueError(f"Time part missing in date string: {standard}")

        date_part = parts[0]
        raw_time = parts[1]

        # Quitar milisegundos o offsets adicionales
        raw_time = re.split(r"[.-]", raw_time)[0]

        clean_str = f"{date_part}T{raw_time}"
        parsed_dt = datetime.fromisoformat(clean_str)
        return cls(parsed_dt)

    def equals(self, other: "Date") -> bool:
        if not isinstance(other, Date):
            return False
        return self._value == other._value

    def Equals(self, other: "Date") -> bool:
        return self.equals(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Date):
            return self._value == other._value
        if isinstance(other, datetime):
            return self._value == other
        return False

    def __str__(self) -> str:
        return self._value.isoformat()

    def __repr__(self) -> str:
        return f"Date({self._value.isoformat()!r})"


def new_date(value: Optional[datetime] = None) -> Date:
    """Constructor helper NewDate."""
    return Date(value)


def NewDate(value: Optional[datetime] = None) -> Date:
    """Alias Go-style para new_date."""
    return new_date(value)


def new_date_now() -> Date:
    """Constructor helper NewDateNow."""
    return Date.now()


def NewDateNow() -> Date:
    """Alias Go-style para new_date_now."""
    return new_date_now()


def date_from_standard_string(standard: str) -> Date:
    """Helper DateFromStandardString."""
    return Date.from_standard_string(standard)


def DateFromStandardString(standard: str) -> Date:
    """Alias Go-style para date_from_standard_string."""
    return date_from_standard_string(standard)

