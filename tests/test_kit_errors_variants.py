import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.errors import (
    DomainError,
    NewAuthorizationError,
    new_authorization_error,
    NewConflictError,
    new_conflict_error,
    NewNotFoundError,
    new_not_found_error,
    NewRateLimitError,
    new_rate_limit_error,
    NewValidationError,
    new_validation_error,
    SerializeError,
    serialize_error,
    AsDomainError,
    as_domain_error,
)


def test_authorization_error():
    err = NewAuthorizationError("Custom forbidden", 401, "Invalid token")
    assert err.err_type == "authorization"
    assert err.message == "Custom forbidden"
    assert err.attributes["status"] == 401
    assert err.attributes["reason"] == "Invalid token"

    default_err = new_authorization_error()
    assert default_err.message == "Not authorized"


def test_conflict_error():
    err = NewConflictError("Email already in use", {"field": "email", "value": "test@example.com"})
    assert err.err_type == "conflict"
    assert err.message == "Email already in use"
    assert err.attributes["details"]["field"] == "email"


def test_not_found_error():
    err = NewNotFoundError("User not found", "User", "usr_123")
    assert err.err_type == "not_found"
    assert err.message == "User not found"
    assert err.attributes["resource"] == "User"
    assert err.attributes["id"] == "usr_123"


def test_rate_limit_error():
    err = NewRateLimitError("ip_1.2.3.4", 100, 60000, 5000)
    assert err.err_type == "rate_limit"
    assert "Rate limit exceeded" in err.message
    assert err.attributes["limit"] == 100
    assert err.attributes["windowMs"] == 60000
    assert err.attributes["retryAfterMs"] == 5000


def test_validation_error():
    err = NewValidationError("Payload invalid", [{"field": "age", "error": "Must be > 0"}])
    assert err.err_type == "validation"
    assert err.message == "Payload invalid"
    assert len(err.attributes["details"]) == 1


def test_serialize_error():
    exc = ValueError("Invalid argument")
    serialized = SerializeError(exc)
    assert serialized["name"] == "ValueError"
    assert serialized["message"] == "Invalid argument"

    obj_err = SerializeError({"error_code": "ERR_1"})
    assert obj_err["name"] == "ObjectThrownError"
    assert "ERR_1" in obj_err["message"]

    assert SerializeError(None) is None


def test_as_domain_error():
    de = NewValidationError("Bad input")
    assert AsDomainError(de) == de

    std_err = RuntimeError("Disk full")
    converted = as_domain_error(std_err)
    assert converted.err_type == "unknown_error"
    assert converted.message == "Disk full"

