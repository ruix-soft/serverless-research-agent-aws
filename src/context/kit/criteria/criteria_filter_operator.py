from enum import Enum


class FilterOperator(str, Enum):
    """
    FilterOperator define los operadores disponibles para filtrar datos.
    Traducción de FilterOperator de Go a Python.
    """

    EQUAL = "="
    NOT_EQUAL = "!="
    GT = ">"
    LT = "<"
    GTOE = ">="
    LTOE = "<="
    IN = "IN"
    NOT_IN = "NOT_IN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    IS = "IS"
    NOT_IS = "NOT_IS"
    OR = "OR"
    BETWEEN = "BETWEEN"
    ARRAY_OVERLAP = "ARRAY_OVERLAP"

    def is_valid(self) -> bool:
        return True

    def IsValid(self) -> bool:
        return self.is_valid()


# Constantes para compatibilidad con Go
FilterOperatorEqual = FilterOperator.EQUAL
FilterOperatorNotEqual = FilterOperator.NOT_EQUAL
FilterOperatorGT = FilterOperator.GT
FilterOperatorLT = FilterOperator.LT
FilterOperatorGTOE = FilterOperator.GTOE
FilterOperatorLTOE = FilterOperator.LTOE
FilterOperatorIn = FilterOperator.IN
FilterOperatorNotIn = FilterOperator.NOT_IN
FilterOperatorContains = FilterOperator.CONTAINS
FilterOperatorNotContains = FilterOperator.NOT_CONTAINS
FilterOperatorIs = FilterOperator.IS
FilterOperatorNotIs = FilterOperator.NOT_IS
FilterOperatorOr = FilterOperator.OR
FilterOperatorBetween = FilterOperator.BETWEEN
FilterOperatorArrayOverlap = FilterOperator.ARRAY_OVERLAP


def new_filter_operator(value: str) -> FilterOperator:
    """
    Crea y valida un FilterOperator a partir de un string.
    """
    for op in FilterOperator:
        if op.value == value or op.name == value.upper():
            return op
    raise ValueError(f"the filter operator {value} is invalid")


def NewFilterOperator(value: str) -> FilterOperator:
    """Alias Go-style para new_filter_operator."""
    return new_filter_operator(value)

