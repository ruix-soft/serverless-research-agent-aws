import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.service import (
    AuditRecord,
    SerializedError,
    NewSerializedError,
    new_serialized_error,
    AuthorizationDecision,
    CacheMissError,
    ErrCacheMiss,
    GoogleTokens,
    GoogleUserInfo,
    CalendarEvent,
    JwtPayload,
    AuthTokens,
    ValidationResult,
)


def test_service_dataclasses_and_constructors():
    auth_dec = AuthorizationDecision(authorized=True, status=200, reason="Granted")
    assert auth_dec.authorized is True
    assert auth_dec.status == 200

    now = datetime.now(timezone.utc)
    record = AuditRecord(type="TestOp", timestamp=now, payload={"k": "v"})
    assert record.type == "TestOp"

    err = new_serialized_error(ValueError("Invalid argument"))
    assert err is not None
    assert err.name == "ValueError"
    assert err.message == "Invalid argument"

    tokens = GoogleTokens(access_token="acc", refresh_token="ref", expires_in=3600)
    assert tokens.access_token == "acc"

    uinfo = GoogleUserInfo(email="test@gmail.com", name="Test User")
    assert uinfo.email == "test@gmail.com"

    cal_event = CalendarEvent(summary="Team Meeting")
    assert cal_event.summary == "Team Meeting"

    jwt_p = JwtPayload(sub="usr_123", scp=["read", "write"])
    assert jwt_p.sub == "usr_123"
    assert "read" in jwt_p.scp

    auth_tok = AuthTokens(access_token="a", refresh_token="r")
    assert auth_tok.access_token == "a"

    val_res = ValidationResult(valid=False, message="Invalid format", details={"field": "email"})
    assert val_res.valid is False
    assert val_res.details["field"] == "email"

    assert isinstance(ErrCacheMiss, CacheMissError)

