from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.rate_limit_error import new_rate_limit_error
from context.kit.service.rate_limiter_service import RateLimiterService

I = TypeVar("I")
O = TypeVar("O")

QueryKeyResolverFn = Callable[[I, str, Optional[Metadata]], str]


@dataclass
class QueryRateLimitOptions(Generic[I]):
    limit: int
    window_ms: int
    key_resolver: QueryKeyResolverFn[I]


class QueryRateLimitDecorator(Generic[I, O], Query[I, O]):
    """
    QueryRateLimitDecorator envuelve una Query para restringir su frecuencia de ejecución.
    """

    def __init__(
        self,
        base: Query[I, O],
        limiter: RateLimiterService,
        options: QueryRateLimitOptions[I],
    ) -> None:
        self._base = base
        self._limiter = limiter
        self._options = options

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryRateLimitDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        meta = self.metadata()
        key = self._options.key_resolver(payload, self.query_type(), meta)

        try:
            allowed = self._limiter.allow(key, self._options.limit, self._options.window_ms, ctx)
        except Exception as exc:
            infra_err = DomainError(
                err_type="rate_limit_infrastructure_error",
                message=f"Failed to check rate limit: {exc}",
            )
            return Result.err(infra_err)

        if not allowed:
            rl_err = new_rate_limit_error(
                key=key,
                limit=self._options.limit,
                window_ms=self._options.window_ms,
            )
            return Result.err(rl_err)

        return self._base.execute(payload, ctx)


def new_query_rate_limit_decorator(
    base: Query[I, O],
    limiter: RateLimiterService,
    options: QueryRateLimitOptions[I],
) -> QueryRateLimitDecorator[I, O]:
    return QueryRateLimitDecorator(base, limiter, options)


def NewQueryRateLimitDecorator(
    base: Query[I, O],
    limiter: RateLimiterService,
    options: QueryRateLimitOptions[I],
) -> QueryRateLimitDecorator[I, O]:
    return new_query_rate_limit_decorator(base, limiter, options)

