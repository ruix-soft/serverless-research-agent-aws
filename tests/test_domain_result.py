import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.validation_error import ValidationError
from context.kit.errors.not_found_error import NotFoundError


def test_result_ok():
    res = Result.ok({"data": 123})
    assert res.is_ok() is True
    assert res.is_err() is False
    assert res.value == {"data": 123}


def test_result_fail():
    err = ValidationError("Invalid input", details={"field": "topic"})
    res = Result.fail(err)
    assert res.is_ok() is False
    assert res.is_err() is True
    assert res.error == err
    assert res.error.to_dict() == {
        "type": "validation",
        "message": "Invalid input",
        "data": {"details": {"field": "topic"}}
    }


def test_domain_error_variants():
    notFound = NotFoundError("Resource not found", resource="Report", id="123")
    assert notFound.err_type == "not_found"
    assert notFound.attributes["resource"] == "Report"


def test_result_map():
    res = Result.ok(10)
    mapped = res.map(lambda x: x * 2)
    assert mapped.is_ok() is True
    assert mapped.value == 20

    err_res = Result.fail(ValidationError("Bad number"))
    mapped_err = err_res.map(lambda x: x * 2)
    assert mapped_err.is_err() is True
    assert mapped_err.error.err_type == "validation"
