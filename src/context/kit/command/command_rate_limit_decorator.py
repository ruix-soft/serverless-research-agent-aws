from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.rate_limit_error import new_rate_limit_error
from context.kit.service.rate_limiter_service import RateLimiterService

I = TypeVar("I")
O = TypeVar("O")

KeyResolverFn = Callable[[I, str, Optional[Metadata]], str]


@dataclass
class RateLimitOptions(Generic[I]):
    limit: int
    window_ms: int
    key_resolver: KeyResolverFn[I]


class CommandRateLimitDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandRateLimitDecorator envuelve un Command para restringir su frecuencia de ejecución.
    """

    def __init__(
        self,
        base: Handler[I, O],
        limiter: RateLimiterService,
        options: RateLimitOptions[I],
    ) -> None:
        self._base = base
        self._limiter = limiter
        self._options = options

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandRateLimitDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        meta = self.metadata()
        key = self._options.key_resolver(payload, self.command_type(), meta)

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


def new_command_rate_limit_decorator(
    base: Handler[I, O],
    limiter: RateLimiterService,
    options: RateLimitOptions[I],
) -> CommandRateLimitDecorator[I, O]:
    return CommandRateLimitDecorator(base, limiter, options)


def NewCommandRateLimitDecorator(
    base: Handler[I, O],
    limiter: RateLimiterService,
    options: RateLimitOptions[I],
) -> CommandRateLimitDecorator[I, O]:
    return new_command_rate_limit_decorator(base, limiter, options)

