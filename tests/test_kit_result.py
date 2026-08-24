import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.result import (
    Result,
    Ok,
    Err,
    ok,
    err,
    ResultMap,
    ResultFold,
    result_map,
    result_fold,
)


def test_result_ok():
    r = Result.ok(100)
    assert r.is_ok() is True
    assert r.IsOk() is True
    assert r.is_error() is False
    assert r.IsError() is False
    assert r.is_err() is False
    assert r.get() == 100
    assert r.Get() == 100
    assert r.value == 100
    assert bool(r) is True

    with pytest.raises(ValueError, match="cannot get error value from ok result"):
        r.get_error()

    with pytest.raises(ValueError, match="cannot get error value from ok result"):
        _ = r.error


def test_result_err():
    r = Result.err("error_code_404")
    assert r.is_ok() is False
    assert r.IsOk() is False
    assert r.is_error() is True
    assert r.IsError() is True
    assert r.is_err() is True
    assert r.get_error() == "error_code_404"
    assert r.GetError() == "error_code_404"
    assert r.error == "error_code_404"
    assert bool(r) is False

    with pytest.raises(ValueError, match="cannot get ok value from error result"):
        r.get()

    with pytest.raises(ValueError, match="cannot get ok value from error result"):
        _ = r.value


def test_result_ok_and_err_helpers():
    r_ok1 = ok("success")
    assert r_ok1.is_ok() is True
    assert r_ok1.get() == "success"

    r_ok2 = Ok("success2")
    assert r_ok2.is_ok() is True
    assert r_ok2.get() == "success2"

    r_err1 = err("failure")
    assert r_err1.is_error() is True
    assert r_err1.get_error() == "failure"

    r_err2 = Err("failure2")
    assert r_err2.is_error() is True
    assert r_err2.get_error() == "failure2"


def test_result_map_method():
    r = Result.ok(10)
    mapped = r.map(lambda x: x * 5)
    assert mapped.is_ok() is True
    assert mapped.get() == 50

    r_err = Result.err("fail")
    mapped_err = r_err.map(lambda x: x * 5)
    assert mapped_err.is_error() is True
    assert mapped_err.get_error() == "fail"


def test_result_map_standalone_helpers():
    r = Ok("antigravity")
    mapped = result_map(r, lambda s: s.upper())
    assert mapped.is_ok() is True
    assert mapped.get() == "ANTIGRAVITY"

    mapped_go = ResultMap(r, lambda s: len(s))
    assert mapped_go.is_ok() is True
    assert mapped_go.get() == 11

    r_err = Err("bad_request")
    mapped_err = ResultMap(r_err, lambda s: len(s))
    assert mapped_err.is_error() is True
    assert mapped_err.get_error() == "bad_request"


def test_result_fold_method():
    r_ok = Result.ok(25)
    result1 = r_ok.fold(
        ok_fn=lambda x: f"Value is {x}",
        error_fn=lambda e: f"Error: {e}",
    )
    assert result1 == "Value is 25"

    r_err = Result.err("database disconnected")
    result2 = r_err.fold(
        ok_fn=lambda x: f"Value is {x}",
        error_fn=lambda e: f"Error: {e}",
    )
    assert result2 == "Error: database disconnected"


def test_result_fold_standalone_helpers():
    r_ok = Ok(42)
    res_ok = result_fold(r_ok, lambda x: x * 2, lambda e: -1)
    assert res_ok == 84

    res_ok_go = ResultFold(r_ok, lambda x: x + 1, lambda e: -1)
    assert res_ok_go == 43

    r_err = Err("network error")
    res_err = ResultFold(r_err, lambda x: x + 1, lambda e: f"caught: {e}")
    assert res_err == "caught: network error"


def test_result_equality_and_repr():
    r1 = Ok(123)
    r2 = Ok(123)
    r3 = Ok(456)
    r_err1 = Err("bad")
    r_err2 = Err("bad")
    r_err3 = Err("other")

    assert r1 == r2
    assert r1 != r3
    assert r1 != r_err1
    assert r_err1 == r_err2
    assert r_err1 != r_err3
    assert r1 != 123

    assert repr(r1) == "Result.ok(123)"
    assert repr(r_err1) == "Result.err('bad')"

