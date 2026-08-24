import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.either import (
    Either,
    NewLeft,
    NewRight,
    new_left,
    new_right,
    Fold,
    Map,
    fold,
    either_map,
)


def test_either_left():
    e = Either.left("left_error")
    assert e.is_left() is True
    assert e.IsLeft() is True
    assert e.is_right() is False
    assert e.IsRight() is False
    assert e.get_left() == "left_error"
    assert e.GetLeft() == "left_error"
    assert bool(e) is False

    with pytest.raises(ValueError, match="cannot get right value from left Either"):
        e.get()

    with pytest.raises(ValueError, match="cannot get right value from left Either"):
        e.Get()


def test_either_right():
    e = Either.right(999)
    assert e.is_left() is False
    assert e.IsLeft() is False
    assert e.is_right() is True
    assert e.IsRight() is True
    assert e.get() == 999
    assert e.Get() == 999
    assert bool(e) is True

    with pytest.raises(ValueError, match="cannot get left value from right Either"):
        e.get_left()

    with pytest.raises(ValueError, match="cannot get left value from right Either"):
        e.GetLeft()


def test_either_factory_helpers():
    e_l1 = new_left("err1")
    assert e_l1.is_left() is True
    assert e_l1.get_left() == "err1"

    e_l2 = NewLeft("err2")
    assert e_l2.is_left() is True
    assert e_l2.get_left() == "err2"

    e_r1 = new_right(123)
    assert e_r1.is_right() is True
    assert e_r1.get() == 123

    e_r2 = NewRight(456)
    assert e_r2.is_right() is True
    assert e_r2.get() == 456


def test_either_map_method():
    e_r = Either.right(10)
    mapped = e_r.map(lambda x: x * 3)
    assert mapped.is_right() is True
    assert mapped.get() == 30

    e_l = Either.left("cannot compute")
    mapped_l = e_l.map(lambda x: x * 3)
    assert mapped_l.is_left() is True
    assert mapped_l.get_left() == "cannot compute"


def test_either_map_standalone_helpers():
    e_r = NewRight("golang")
    mapped = either_map(e_r, lambda s: s.upper())
    assert mapped.is_right() is True
    assert mapped.get() == "GOLANG"

    mapped_go = Map(e_r, lambda s: len(s))
    assert mapped_go.is_right() is True
    assert mapped_go.get() == 6

    e_l = NewLeft("error")
    mapped_l = Map(e_l, lambda s: len(s))
    assert mapped_l.is_left() is True
    assert mapped_l.get_left() == "error"


def test_either_fold_method():
    e_r = Either.right(50)
    res_r = e_r.fold(
        left_fn=lambda l: f"Left: {l}",
        right_fn=lambda r: f"Right: {r}",
    )
    assert res_r == "Right: 50"

    e_l = Either.left("not found")
    res_l = e_l.fold(
        left_fn=lambda l: f"Left: {l}",
        right_fn=lambda r: f"Right: {r}",
    )
    assert res_l == "Left: not found"


def test_either_fold_standalone_helpers():
    e_r = NewRight(100)
    res_r = fold(e_r, lambda l: -1, lambda r: r * 2)
    assert res_r == 200

    res_r_go = Fold(e_r, lambda l: -1, lambda r: r + 5)
    assert res_r_go == 105

    e_l = NewLeft("fail")
    res_l = Fold(e_l, lambda l: f"error: {l}", lambda r: str(r))
    assert res_l == "error: fail"


def test_either_equality_and_repr():
    l1 = Either.left("abc")
    l2 = Either.left("abc")
    l3 = Either.left("xyz")

    r1 = Either.right(10)
    r2 = Either.right(10)
    r3 = Either.right(20)

    assert l1 == l2
    assert l1 != l3
    assert l1 != r1
    assert r1 == r2
    assert r1 != r3
    assert r1 != 10

    assert repr(l1) == "Either.left('abc')"
    assert repr(r1) == "Either.right(10)"

