import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.errors.domain_error import (
    DomainError,
    NewDomainError,
    new_domain_error,
)


def test_domain_error_creation_and_getters():
    err = NewDomainError(
        err_type="user_not_found",
        message="User with ID 123 does not exist",
        attributes={"user_id": 123},
    )

    assert err.err_type == "user_not_found"
    assert err.type == "user_not_found"
    assert err.Type() == "user_not_found"
    assert err.message == "User with ID 123 does not exist"
    assert err.Message() == "User with ID 123 does not exist"
    assert err.error() == "User with ID 123 does not exist"
    assert err.Error() == "User with ID 123 does not exist"
    assert err.attributes == {"user_id": 123}
    assert err.Attributes() == {"user_id": 123}
    assert str(err) == "User with ID 123 does not exist"


def test_domain_error_to_primitives():
    err = new_domain_error(
        err_type="invalid_input",
        message="Field topic is required",
        attributes={"field": "topic"},
    )

    primitives = err.to_primitives()
    assert primitives == {
        "type": "invalid_input",
        "message": "Field topic is required",
        "data": {"field": "topic"},
    }
    assert err.ToPrimitives() == primitives
    assert err.to_dict() == primitives


def test_domain_error_from_primitives():
    data = {
        "type": "unauthorized",
        "message": "Token expired",
        "data": {"expired_at": "2026-08-24T12:00:00Z"},
    }
    err = DomainError.from_primitives(data)
    assert err.err_type == "unauthorized"
    assert err.message == "Token expired"
    assert err.attributes == {"expired_at": "2026-08-24T12:00:00Z"}


def test_domain_error_as_exception():
    with pytest.raises(DomainError) as exc_info:
        raise NewDomainError("internal_error", "Something went wrong", None)

    assert exc_info.value.err_type == "internal_error"
    assert exc_info.value.attributes == {}

