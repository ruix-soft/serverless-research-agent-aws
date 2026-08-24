from dataclasses import dataclass
from typing import List, Sequence, Union, Optional, Any, Dict
from context.kit.criteria.criteria_order_by import OrderBy, new_order_by
from context.kit.criteria.criteria_order_type import OrderType, OrderTypeAsc, OrderTypeDesc, new_order_type


@dataclass
class OrderPrimitive:
    field: str
    direction: str = "asc"


class Order:
    """
    Order representa un criterio de ordenamiento (Campo + Dirección).
    """

    def __init__(self, order_by: OrderBy, order_type: OrderType) -> None:
        self._order_by = order_by
        self._order_type = order_type

    @classmethod
    def from_primitives(cls, primitives: Sequence[Union[OrderPrimitive, Dict[str, Any], Sequence[str]]]) -> List["Order"]:
        if not primitives:
            return []

        orders: List[Order] = []
        for p in primitives:
            if isinstance(p, OrderPrimitive):
                field = p.field
                dir_str = p.direction or "asc"
            elif isinstance(p, dict):
                field = p.get("field") or p.get("orderBy") or p.get("Field") or ""
                dir_str = p.get("direction") or p.get("orderType") or p.get("Direction") or "asc"
            elif isinstance(p, (list, tuple)) and len(p) >= 2:
                field = p[0]
                dir_str = p[1]
            elif isinstance(p, (list, tuple)) and len(p) == 1:
                field = p[0]
                dir_str = "asc"
            else:
                continue

            ot = new_order_type(dir_str)
            ob = new_order_by(field)
            orders.append(cls(ob, ot))

        return orders

    @classmethod
    def none(cls) -> List["Order"]:
        return []

    @classmethod
    def desc(cls, fields: Sequence[str]) -> List["Order"]:
        return [cls(new_order_by(f), OrderTypeDesc) for f in fields]

    @classmethod
    def asc(cls, fields: Sequence[str]) -> List["Order"]:
        return [cls(new_order_by(f), OrderTypeAsc) for f in fields]

    def has_order(self) -> bool:
        return not self._order_type.is_none()

    def HasOrder(self) -> bool:
        return self.has_order()

    def order_by(self) -> OrderBy:
        return self._order_by

    def OrderBy(self) -> OrderBy:
        return self.order_by()

    def order_type(self) -> OrderType:
        return self._order_type

    def OrderType(self) -> OrderType:
        return self.order_type()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return False
        return self._order_by == other._order_by and self._order_type == other._order_type

    def __repr__(self) -> str:
        return f"Order(order_by={self._order_by!r}, order_type={self._order_type!r})"


def new_order(order_by: OrderBy, order_type: OrderType) -> Order:
    return Order(order_by, order_type)


def NewOrder(order_by: OrderBy, order_type: OrderType) -> Order:
    return new_order(order_by, order_type)


def new_orders_from_primitives(primitives: Sequence[Any]) -> List[Order]:
    return Order.from_primitives(primitives)


def NewOrdersFromPrimitives(primitives: Sequence[Any]) -> List[Order]:
    return new_orders_from_primitives(primitives)


def new_orders_none() -> List[Order]:
    return Order.none()


def NewOrdersNone() -> List[Order]:
    return new_orders_none()


def new_orders_desc(fields: Sequence[str]) -> List[Order]:
    return Order.desc(fields)


def NewOrdersDesc(fields: Sequence[str]) -> List[Order]:
    return new_orders_desc(fields)


def new_orders_asc(fields: Sequence[str]) -> List[Order]:
    return Order.asc(fields)


def NewOrdersAsc(fields: Sequence[str]) -> List[Order]:
    return new_orders_asc(fields)

