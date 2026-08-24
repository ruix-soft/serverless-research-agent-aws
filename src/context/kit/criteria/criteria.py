from typing import List, Optional, Sequence
from context.kit.criteria.criteria_filters import Filters, new_filters_none
from context.kit.criteria.criteria_order import Order, new_orders_none


class Criteria:
    """
    Criteria agrupa filtros, ordenamiento y paginación (limit/offset) para consultas de datos.
    Traducción de Criteria struct de Go a Python.
    """

    def __init__(
        self,
        filters: Optional[Filters] = None,
        orders: Optional[Sequence[Order]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> None:
        self._filters: Filters = filters if filters is not None else new_filters_none()
        self._orders: List[Order] = list(orders) if orders is not None else new_orders_none()
        self._limit: Optional[int] = limit
        self._offset: Optional[int] = offset

    @classmethod
    def empty(cls) -> "Criteria":
        return cls()

    @classmethod
    def NewEmptyCriteria(cls) -> "Criteria":
        return cls.empty()

    def with_limit(self, limit: int) -> "Criteria":
        """Retorna una copia de Criteria con el límite establecido."""
        return Criteria(
            filters=self._filters,
            orders=self._orders,
            limit=limit,
            offset=self._offset,
        )

    def WithLimit(self, limit: int) -> "Criteria":
        return self.with_limit(limit)

    def with_offset(self, offset: int) -> "Criteria":
        """Retorna una copia de Criteria con el offset establecido."""
        return Criteria(
            filters=self._filters,
            orders=self._orders,
            limit=self._limit,
            offset=offset,
        )

    def WithOffset(self, offset: int) -> "Criteria":
        return self.with_offset(offset)

    def filters(self) -> Filters:
        return self._filters

    def Filters(self) -> Filters:
        return self.filters()

    def orders(self) -> List[Order]:
        return list(self._orders)

    def Orders(self) -> List[Order]:
        return self.orders()

    def limit(self) -> Optional[int]:
        return self._limit

    def Limit(self) -> Optional[int]:
        return self.limit()

    def offset(self) -> Optional[int]:
        return self._offset

    def Offset(self) -> Optional[int]:
        return self.offset()

    def has_filters(self) -> bool:
        return not self._filters.is_empty()

    def HasFilters(self) -> bool:
        return self.has_filters()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Criteria):
            return False
        return (
            self._filters == other._filters
            and self._orders == other._orders
            and self._limit == other._limit
            and self._offset == other._offset
        )

    def __repr__(self) -> str:
        return (
            f"Criteria(filters={self._filters!r}, "
            f"orders={self._orders!r}, "
            f"limit={self._limit!r}, "
            f"offset={self._offset!r})"
        )


def new_criteria(
    filters: Optional[Filters] = None,
    orders: Optional[Sequence[Order]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Criteria:
    return Criteria(filters=filters, orders=orders, limit=limit, offset=offset)


def NewCriteria(
    filters: Optional[Filters] = None,
    orders: Optional[Sequence[Order]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Criteria:
    return new_criteria(filters=filters, orders=orders, limit=limit, offset=offset)


def new_empty_criteria() -> Criteria:
    return Criteria.empty()


def NewEmptyCriteria() -> Criteria:
    return new_empty_criteria()

