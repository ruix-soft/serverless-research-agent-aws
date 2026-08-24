from abc import ABC, abstractmethod
from typing import Optional, Any


class TransactionManagerService(ABC):
    """
    TransactionManagerService define el contrato para manejar transacciones de base de datos.
    """

    @abstractmethod
    def begin(self, ctx: Optional[Any] = None) -> Any:
        """Inicia una transacción y retorna el contexto transaccional."""
        pass

    def Begin(self, ctx: Optional[Any] = None) -> Any:
        return self.begin(ctx)

    @abstractmethod
    def commit(self, ctx: Optional[Any] = None) -> None:
        """Confirma la transacción."""
        pass

    def Commit(self, ctx: Optional[Any] = None) -> None:
        self.commit(ctx)

    @abstractmethod
    def rollback(self, ctx: Optional[Any] = None, err: Optional[Any] = None) -> None:
        """Revierte la transacción."""
        pass

    def Rollback(self, ctx: Optional[Any] = None, err: Optional[Any] = None) -> None:
        self.rollback(ctx, err)

