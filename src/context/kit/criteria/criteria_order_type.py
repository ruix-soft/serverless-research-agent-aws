from enum import Enum


class OrderType(str, Enum):
    """
    OrderType define la dirección del ordenamiento (ASC, DESC, NONE).
    """

    ASC = "asc"
    DESC = "desc"
    NONE = "none"

    def is_none(self) -> bool:
        return self == OrderType.NONE

    def IsNone(self) -> bool:
        return self.is_none()

    def is_asc(self) -> bool:
        return self == OrderType.ASC

    def IsAsc(self) -> bool:
        return self.is_asc()

    def is_desc(self) -> bool:
        return self == OrderType.DESC

    def IsDesc(self) -> bool:
        return self.is_desc()


# Constantes para compatibilidad con Go
OrderTypeAsc = OrderType.ASC
OrderTypeDesc = OrderType.DESC
OrderTypeNone = OrderType.NONE


def new_order_type(value: str) -> OrderType:
    v = str(value).lower()
    if v == "asc":
        return OrderType.ASC
    if v == "desc":
        return OrderType.DESC
    if v == "none":
        return OrderType.NONE
    raise ValueError(f"the criteria order type {value} is invalid")


def NewOrderType(value: str) -> OrderType:
    """Alias Go-style para new_order_type."""
    return new_order_type(value)

