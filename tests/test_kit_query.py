import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.query import (
    Query,
    BaseQuery,
    NewBaseQuery,
    new_base_query,
    QueryAuditDecorator,
    QueryAuthorizationDecorator,
    QueryAuthorizationOptions,
    QueryCacheDecorator,
    QueryCacheOptions,
    QueryLoggingDecorator,
    QueryMetricsDecorator,
    QueryRateLimitDecorator,
    QueryRateLimitOptions,
    QueryValidationDecorator,
    QueryValidationOptions,
)
from context.kit.dtos.metadata import NewMetadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, NewDomainError
from context.kit.service.cache_service import CacheService
from context.kit.service.audit_service import AuditService, AuditRecord
from context.kit.service.authorization_service import AuthorizationService, AuthorizationDecision
from context.kit.service.logger_service import LoggerService
from context.kit.service.metrics_service import MetricsService
from context.kit.service.rate_limiter_service import RateLimiterService
from context.kit.service.validation_service import ValidationService, ValidationResult


class SimpleQueryHandler(Query[str, str], BaseQuery):
    def __init__(self):
        BaseQuery.__init__(self, "SimpleQuery", NewMetadata("query_user"))

    def execute(self, payload: str, ctx=None) -> Result[str, DomainError]:
        if payload == "fail":
            return Result.err(NewDomainError("query_failed", "Intentional failure"))
        return Result.ok(f"query_result: {payload}")


class MockCache(CacheService):
    def __init__(self):
        self.store = {}

    def get(self, key: str, ctx=None):
        return self.store.get(key)

    def set(self, key: str, value, ttl=None, ctx=None):
        self.store[key] = value

    def invalidate(self, key: str, ctx=None):
        self.store.pop(key, None)


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


class MockLogger(LoggerService):
    def __init__(self):
        self.logs = []

    def info(self, message: str, details=None):
        self.logs.append(("INFO", message))

    def warn(self, message: str, details=None):
        self.logs.append(("WARN", message))

    def debug(self, message: str, details=None):
        self.logs.append(("DEBUG", message))

    def error(self, message: str, err=None, details=None):
        self.logs.append(("ERROR", message))


class MockMetrics(MetricsService):
    def __init__(self):
        self.metrics = []

    def add_dimension(self, name: str, value: str):
        pass

    def add_metric(self, name: str, unit, value: float):
        self.metrics.append((name, unit, value))

    def publish_stored_metrics(self, ctx=None):
        pass


class MockRateLimiter(RateLimiterService):
    def __init__(self, is_allowed=True):
        self._is_allowed = is_allowed

    def allow(self, key, limit, window_ms, ctx=None):
        return self._is_allowed


class MockValidator(ValidationService):
    def __init__(self, valid=True):
        self.valid = valid

    def validate(self, payload, validation_type, metadata=None, ctx=None):
        return ValidationResult(valid=self.valid, message="Validation error" if not self.valid else None)


def test_base_query():
    meta = NewMetadata("admin")
    bq = NewBaseQuery("GetUsers", meta)
    assert bq.query_type() == "GetUsers"
    assert bq.Type() == "GetUsers"
    assert bq.metadata() == meta
    assert bq.Metadata() == meta


def test_query_cache_decorator():
    cache = MockCache()
    query = SimpleQueryHandler()
    options = QueryCacheOptions(key_generator=lambda p, q: f"cache_{p}")
    dec = QueryCacheDecorator(query, cache, options)

    res1 = dec.execute("item_1")
    assert res1.is_ok() is True
    assert res1.get() == "query_result: item_1"
    assert cache.store.get("cache_item_1") == "query_result: item_1"

    cache.store["cache_item_1"] = "cached_override"
    res2 = dec.execute("item_1")
    assert res2.get() == "cached_override"


def test_query_audit_decorator():
    audit = MockAudit()
    query = SimpleQueryHandler()
    dec = QueryAuditDecorator(query, audit)

    res = dec.execute("data")
    assert res.is_ok() is True
    assert len(audit.records) == 1
    assert audit.records[0].type == "SimpleQuery"


def test_query_auth_decorator():
    auth_ok = MockAuth(allow=True)
    auth_denied = MockAuth(allow=False)
    query = SimpleQueryHandler()

    dec_ok = QueryAuthorizationDecorator(query, auth_ok)
    assert dec_ok.execute("ok").is_ok() is True

    dec_denied = QueryAuthorizationDecorator(query, auth_denied)
    res_denied = dec_denied.execute("ok")
    assert res_denied.is_error() is True
    assert res_denied.get_error().err_type == "authorization"


def test_query_logging_and_metrics_decorator():
    logger = MockLogger()
    metrics = MockMetrics()
    query = SimpleQueryHandler()

    dec = QueryMetricsDecorator(QueryLoggingDecorator(query, logger), metrics)
    res = dec.execute("val")

    assert res.is_ok() is True
    assert len(logger.logs) >= 2
    assert len(metrics.metrics) >= 2


def test_query_rate_limit_and_validation_decorators():
    limiter = MockRateLimiter(is_allowed=False)
    query = SimpleQueryHandler()
    rl_dec = QueryRateLimitDecorator(query, limiter, QueryRateLimitOptions(limit=1, window_ms=1000, key_resolver=lambda p, t, m: "k"))
    assert rl_dec.execute("val").is_error() is True

    val_fail = MockValidator(valid=False)
    val_dec = QueryValidationDecorator(query, val_fail)
    assert val_dec.execute("val").is_error() is True
