from dataclasses import dataclass
from typing import List, Sequence, Union, Any, Dict
from context.kit.criteria.criteria_filter import Filter, new_filter_from_primitives


@dataclass
class FilterPrimitive:
    field: str
    operator: str
    value: Any


class Filters:
    """
    Filters representa una colección de filtros de búsqueda.
    """

    def __init__(self, filters: Sequence[Filter]) -> None:
        self._filters: List[Filter] = list(filters)

    @classmethod
    def none(cls) -> "Filters":
        return cls([])

    @classmethod
    def from_primitives(cls, primitives: Sequence[Union[FilterPrimitive, Dict[str, Any], Sequence[Any]]]) -> "Filters":
        list_filters: List[Filter] = []
        for p in primitives:
            if isinstance(p, FilterPrimitive):
                f = new_filter_from_primitives(p.field, p.operator, p.value)
            elif isinstance(p, dict):
                f = new_filter_from_primitives(
                    p.get("field") or p.get("Field") or "",
                    p.get("operator") or p.get("Operator") or "=",
                    p.get("value") if "value" in p else p.get("Value"),
                )
            elif isinstance(p, (list, tuple)) and len(p) >= 3:
                f = new_filter_from_primitives(p[0], p[1], p[2])
            else:
                continue
            list_filters.append(f)
        return cls(list_filters)

    def values(self) -> List[Filter]:
        return list(self._filters)

    def Values(self) -> List[Filter]:
        return self.values()

    def is_empty(self) -> bool:
        return len(self._filters) == 0

    def IsEmpty(self) -> bool:
        return self.is_empty()

    def __iter__(self):
        return iter(self._filters)

    def __len__(self) -> int:
        return len(self._filters)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filters):
            return False
        return self._filters == other._filters

    def __repr__(self) -> str:
        return f"Filters({self._filters!r})"


def new_filters(filters: Sequence[Filter]) -> Filters:
    return Filters(filters)


def NewFilters(filters: Sequence[Filter]) -> Filters:
    return new_filters(filters)


def new_filters_none() -> Filters:
    return Filters.none()


def NewFiltersNone() -> Filters:
    return new_filters_none()


def new_filters_from_primitives(primitives: Sequence[Any]) -> Filters:
    return Filters.from_primitives(primitives)


def NewFiltersFromPrimitives(primitives: Sequence[Any]) -> Filters:
    return new_filters_from_primitives(primitives)

