import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.optional import (
    Optional,
    OptionalOf,
    OptionalEmpty,
    OptionalMap,
    optional_of,
    optional_empty,
    optional_map,
)


def test_optional_of_and_is_present():
    opt = Optional.of("hello")
    assert opt.is_present() is True
    assert opt.IsPresent() is True
    assert opt.is_empty() is False
    assert opt.IsEmpty() is False
    assert opt.get() == "hello"
    assert opt.Get() == "hello"
    assert bool(opt) is True


def test_optional_empty():
    opt = Optional.empty()
    assert opt.is_present() is False
    assert opt.IsPresent() is False
    assert opt.is_empty() is True
    assert opt.IsEmpty() is True
    assert bool(opt) is False

    with pytest.raises(ValueError, match="Cannot get value from an empty Optional"):
        opt.get()

    with pytest.raises(ValueError, match="Cannot get value from an empty Optional"):
        opt.Get()


def test_optional_of_function_helpers():
    opt1 = optional_of(42)
    assert opt1.is_present() is True
    assert opt1.get() == 42

    opt2 = OptionalOf(42)
    assert opt2.is_present() is True
    assert opt2.get() == 42

    empty1 = optional_empty()
    assert empty1.is_empty() is True

    empty2 = OptionalEmpty()
    assert empty2.is_empty() is True


def test_optional_or_else():
    opt = Optional.of("present")
    assert opt.or_else("fallback") == "present"
    assert opt.OrElse("fallback") == "present"

    empty = Optional.empty()
    assert empty.or_else("fallback") == "fallback"
    assert empty.OrElse("fallback") == "fallback"


def test_optional_or_else_get():
    opt = Optional.of(100)
    assert opt.or_else_get(lambda: 200) == 100
    assert opt.OrElseGet(lambda: 200) == 100

    empty = Optional.empty()
    assert empty.or_else_get(lambda: 200) == 200
    assert empty.OrElseGet(lambda: 200) == 200


def test_optional_or_else_throw():
    opt = Optional.of("value")
    assert opt.or_else_throw() == "value"
    assert opt.OrElseThrow() == "value"
    assert opt.or_else_throw(RuntimeError("custom error")) == "value"

    empty = Optional.empty()

    # Default exception
    with pytest.raises(ValueError, match="Value is not present in Optional"):
        empty.or_else_throw()

    # Exception instance
    with pytest.raises(KeyError, match="Missing key"):
        empty.or_else_throw(KeyError("Missing key"))

    # Exception class
    with pytest.raises(TypeError):
        empty.or_else_throw(TypeError)

    # Callable / factory returning exception
    with pytest.raises(ValueError, match="Custom supplier error"):
        empty.OrElseThrow(lambda: ValueError("Custom supplier error"))


def test_optional_map_method():
    opt = Optional.of(5)
    mapped = opt.map(lambda x: x * 3)
    assert mapped.is_present() is True
    assert mapped.get() == 15

    empty = Optional.empty()
    mapped_empty = empty.map(lambda x: x * 3)
    assert mapped_empty.is_empty() is True


def test_optional_map_standalone_helper():
    opt = Optional.of("abc")
    mapped = optional_map(opt, lambda s: s.upper())
    assert mapped.is_present() is True
    assert mapped.get() == "ABC"

    mapped_go = OptionalMap(opt, lambda s: len(s))
    assert mapped_go.is_present() is True
    assert mapped_go.get() == 3

    empty = Optional.empty()
    mapped_empty = OptionalMap(empty, lambda s: len(s))
    assert mapped_empty.is_empty() is True


def test_optional_equality_and_repr():
    opt1 = Optional.of(10)
    opt2 = Optional.of(10)
    opt3 = Optional.of(20)
    empty1 = Optional.empty()
    empty2 = Optional.empty()

    assert opt1 == opt2
    assert opt1 != opt3
    assert opt1 != empty1
    assert empty1 == empty2
    assert opt1 != 10

    assert repr(opt1) == "Optional.of(10)"
    assert repr(empty1) == "Optional.empty()"

