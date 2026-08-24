from dataclasses import dataclass
from datetime import timedelta
from typing import Generic, TypeVar, Optional, Any, Callable
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.cache_service import CacheService

I = TypeVar("I")
O = TypeVar("O")

CacheKeyGeneratorFn = Callable[[I, str], str]


@dataclass
class QueryCacheOptions(Generic[I]):
    key_generator: CacheKeyGeneratorFn[I]
    ttl: Optional[timedelta] = None


class QueryCacheDecorator(Generic[I, O], Query[I, O]):
    """
    QueryCacheDecorator envuelve una Query para almacenar en caché las respuestas exitosas.
    """

    def __init__(
        self,
        base: Query[I, O],
        cache: CacheService,
        options: QueryCacheOptions[I],
    ) -> None:
        self._base = base
        self._cache = cache
        self._options = options

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryCacheDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        key = self._options.key_generator(payload, self.query_type())

        try:
            cached_val = self._cache.get(key, ctx)
            if cached_val is not None:
                return Result.ok(cached_val)
        except Exception:
            pass

        result = self._base.execute(payload, ctx)

        if result.is_ok():
            try:
                self._cache.set(key, result.get(), self._options.ttl, ctx)
            except Exception:
                pass

        return result


def new_query_cache_decorator(
    base: Query[I, O],
    cache: CacheService,
    options: QueryCacheOptions[I],
) -> QueryCacheDecorator[I, O]:
    return QueryCacheDecorator(base, cache, options)


def NewQueryCacheDecorator(
    base: Query[I, O],
    cache: CacheService,
    options: QueryCacheOptions[I],
) -> QueryCacheDecorator[I, O]:
    return new_query_cache_decorator(base, cache, options)

