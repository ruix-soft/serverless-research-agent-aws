import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.command import (
    Handler,
    BaseHandler,
    CommandAuditDecorator,
    CommandAuthorizationDecorator,
    CommandAuthorizationOptions,
    CommandLoggingDecorator,
    CommandMetricsDecorator,
    CommandRateLimitDecorator,
    RateLimitOptions,
    CommandTransactionalDecorator,
    TransactionalOptions,
    CommandValidationDecorator,
    ValidationOptions,
)
from context.kit.dtos.metadata import NewMetadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, NewDomainError
from context.kit.service.audit_service import AuditService, AuditRecord
from context.kit.service.authorization_service import AuthorizationService, AuthorizationDecision
from context.kit.service.logger_service import LoggerService
from context.kit.service.metrics_service import MetricsService
from context.kit.service.rate_limiter_service import RateLimiterService
from context.kit.service.transaction_manager_service import TransactionManagerService
from context.kit.service.validation_service import ValidationService, ValidationResult


class SimpleCommandHandler(Handler[str, str], BaseHandler):
    def __init__(self):
        BaseHandler.__init__(self, "SimpleCommand", NewMetadata("test_user"))

    def execute(self, payload: str, ctx=None) -> Result[str, DomainError]:
        if payload == "fail":
            return Result.err(NewDomainError("command_failed", "Intentional failure"))
        return Result.ok(f"processed: {payload}")


class MockAudit(AuditService):
    def __init__(self):
        self.records = []

    def record(self, entry: AuditRecord, ctx=None):
        self.records.append(entry)


class MockAuth(AuthorizationService):
    def __init__(self, allow=True):
        self.allow = allow

    def authorize(self, payload, action_type, metadata=None, ctx=None):
        return AuthorizationDecision(authorized=self.allow, reason="Forbidden" if not self.allow else None)


class MockRateLimiter(RateLimiterService):
    def __init__(self, is_allowed=True):
        self._is_allowed = is_allowed

    def allow(self, key, limit, window_ms, ctx=None):
        return self._is_allowed


class MockTx(TransactionManagerService):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def begin(self, ctx=None):
        return {"tx": True}

    def commit(self, ctx=None):
        self.committed = True

    def rollback(self, ctx=None, err=None):
        self.rolled_back = True


class MockValidator(ValidationService):
    def __init__(self, valid=True):
        self.valid = valid

    def validate(self, payload, validation_type, metadata=None, ctx=None):
        return ValidationResult(valid=self.valid, message="Validation error" if not self.valid else None)


def test_command_audit_decorator():
    audit = MockAudit()
    cmd = SimpleCommandHandler()
    decorated = CommandAuditDecorator(cmd, audit)

    res = decorated.execute("input_data")
    assert res.is_ok() is True
    assert len(audit.records) == 1
    assert audit.records[0].type == "SimpleCommand"
    assert audit.records[0].result == "processed: input_data"


def test_command_auth_decorator():
    auth_allowed = MockAuth(allow=True)
    auth_denied = MockAuth(allow=False)
    cmd = SimpleCommandHandler()

    dec_allowed = CommandAuthorizationDecorator(cmd, auth_allowed)
    assert dec_allowed.execute("ok").is_ok() is True

    dec_denied = CommandAuthorizationDecorator(cmd, auth_denied)
    res_denied = dec_denied.execute("ok")
    assert res_denied.is_error() is True
    assert res_denied.get_error().err_type == "authorization"


def test_command_rate_limit_decorator():
    limiter = MockRateLimiter(is_allowed=False)
    cmd = SimpleCommandHandler()
    options = RateLimitOptions(limit=5, window_ms=1000, key_resolver=lambda p, t, m: "user_key")
    dec = CommandRateLimitDecorator(cmd, limiter, options)

    res = dec.execute("payload")
    assert res.is_error() is True
    assert res.get_error().err_type == "rate_limit"


def test_command_transactional_decorator():
    tx = MockTx()
    cmd = SimpleCommandHandler()
    dec = CommandTransactionalDecorator(cmd, tx)

    res_ok = dec.execute("success")
    assert res_ok.is_ok() is True
    assert tx.committed is True

    tx_fail = MockTx()
    dec_fail = CommandTransactionalDecorator(cmd, tx_fail)
    res_fail = dec_fail.execute("fail")
    assert res_fail.is_error() is True
    assert tx_fail.rolled_back is True


def test_command_validation_decorator():
    val_pass = MockValidator(valid=True)
    val_fail = MockValidator(valid=False)
    cmd = SimpleCommandHandler()

    assert CommandValidationDecorator(cmd, val_pass).execute("valid").is_ok() is True

    res_fail = CommandValidationDecorator(cmd, val_fail).execute("invalid")
    assert res_fail.is_error() is True
    assert res_fail.get_error().err_type == "validation"
