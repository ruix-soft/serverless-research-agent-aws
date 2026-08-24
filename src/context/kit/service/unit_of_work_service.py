from abc import ABC, abstractmethod
from typing import Callable, Optional, Any
from context.kit.dtos.metadata import Metadata

UnitOfWorkBlock = Callable[[Optional[Any]], Any]


class UnitOfWorkService(ABC):
    """
    UnitOfWorkService define la API de alto nivel para transacciones atómicas.
    """

    @abstractmethod
    def run_in_transaction(
        self,
        fn: UnitOfWorkBlock,
        ctx: Optional[Any] = None,
    ) -> Any:
        pass

    def RunInTransaction(
        self,
        ctx: Optional[Any],
        fn: UnitOfWorkBlock,
    ) -> Any:
        return self.run_in_transaction(fn, ctx)

    def run_in_transaction_with_meta(
        self,
        fn: UnitOfWorkBlock,
        meta: Optional[Metadata] = None,
        ctx: Optional[Any] = None,
    ) -> Any:
        return self.run_in_transaction(fn, ctx)

    def RunInTransactionWithMeta(
        self,
        ctx: Optional[Any],
        meta: Optional[Metadata],
        fn: UnitOfWorkBlock,
    ) -> Any:
        return self.run_in_transaction_with_meta(fn, meta, ctx)

