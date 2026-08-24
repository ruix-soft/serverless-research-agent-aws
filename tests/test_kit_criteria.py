import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.criteria import (
    FilterField,
    NewFilterField,
    FilterOperator,
    NewFilterOperator,
    FilterValue,
    NewFilterValue,
    Filter,
    NewFilter,
    NewFilterFromPrimitives,
    Filters,
    FilterPrimitive,
    NewFilters,
    NewFiltersNone,
    NewFiltersFromPrimitives,
    OrderBy,
    NewOrderBy,
    OrderType,
    NewOrderType,
    OrderTypeAsc,
    OrderTypeDesc,
    Order,
    NewOrder,
    NewOrdersAsc,
    NewOrdersDesc,
    NewOrdersFromPrimitives,
    Criteria,
    NewCriteria,
    NewEmptyCriteria,
)


def test_criteria_filter_primitives_and_validation():
    f = NewFilterFromPrimitives("status", "=", "ACTIVE")
    assert f.field().value() == "status"
    assert f.operator() == FilterOperator.EQUAL
    assert f.value().value() == "ACTIVE"

    with pytest.raises(ValueError, match="the field is required"):
        NewFilterFromPrimitives("", "=", "val")

    with pytest.raises(ValueError, match="is invalid"):
        NewFilterFromPrimitives("status", "INVALID_OP", "val")


def test_criteria_filters_collection():
    f1 = NewFilterFromPrimitives("age", ">", 18)
    f2 = NewFilterFromPrimitives("country", "IN", ["ES", "MX"])
    filters = NewFilters([f1, f2])

    assert len(filters) == 2
    assert filters.is_empty() is False
    assert filters.IsEmpty() is False

    empty_filters = NewFiltersNone()
    assert empty_filters.is_empty() is True

    from_prims = NewFiltersFromPrimitives([
        FilterPrimitive("email", "CONTAINS", "@domain.com"),
        {"field": "verified", "operator": "=", "value": True},
        ("score", ">=", 90),
    ])
    assert len(from_prims) == 3


def test_criteria_order():
    orders = NewOrdersFromPrimitives([
        ("created_at", "desc"),
        {"field": "name", "direction": "asc"},
    ])
    assert len(orders) == 2
    assert orders[0].order_by().value() == "created_at"
    assert orders[0].order_type() == OrderTypeDesc
    assert orders[1].order_by().value() == "name"
    assert orders[1].order_type() == OrderTypeAsc

    asc_orders = NewOrdersAsc(["name", "age"])
    assert len(asc_orders) == 2
    assert asc_orders[0].order_type() == OrderTypeAsc

    desc_orders = NewOrdersDesc(["rating"])
    assert len(desc_orders) == 1
    assert desc_orders[0].order_type() == OrderTypeDesc


def test_criteria_full_structure():
    empty_c = NewEmptyCriteria()
    assert empty_c.has_filters() is False
    assert empty_c.HasFilters() is False
    assert empty_c.limit() is None
    assert empty_c.offset() is None

    filters = NewFiltersFromPrimitives([("role", "=", "admin")])
    orders = NewOrdersDesc(["last_login"])
    c = NewCriteria(filters=filters, orders=orders, limit=20, offset=40)

    assert c.has_filters() is True
    assert c.limit() == 20
    assert c.offset() == 40

    c_modified = c.with_limit(50).with_offset(100)
    assert c_modified.limit() == 50
    assert c_modified.offset() == 100
    # Inmutabilidad
    assert c.limit() == 20

