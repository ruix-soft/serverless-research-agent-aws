from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.service.transaction_manager_service import TransactionManagerService

I = TypeVar("I")
O = TypeVar("O")


@dataclass
class TransactionalOptions:
    disable_rollback_on_result_error: bool = False
    disable_rollback_on_panic: bool = False


class CommandTransactionalDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandTransactionalDecorator envuelve un Command en una transacción de base de datos.
    """

    def __init__(
        self,
        base: Handler[I, O],
        tx: TransactionManagerService,
        options: Optional[TransactionalOptions] = None,
    ) -> None:
        self._base = base
        self._tx = tx
        self._options = options or TransactionalOptions()

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandTransactionalDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        try:
            tx_ctx = self._tx.begin(ctx)
        except Exception as exc:
            infra_err = DomainError("transaction_begin_error", str(exc))
            return Result.err(infra_err)

        try:
            result = self._base.execute(payload, tx_ctx)
        except Exception as exc:
            if not self._options.disable_rollback_on_panic:
                try:
                    self._tx.rollback(tx_ctx, exc)
                except Exception:
                    pass
            raise

        if result.is_error():
            if not self._options.disable_rollback_on_result_error:
                try:
                    self._tx.rollback(tx_ctx, result.get_error())
                except Exception:
                    pass
            else:
                try:
                    self._tx.commit(tx_ctx)
                except Exception:
                    pass
            return result

        try:
            self._tx.commit(tx_ctx)
        except Exception as exc:
            commit_err = DomainError("transaction_commit_error", str(exc))
            return Result.err(commit_err)

        return result


def new_command_transactional_decorator(
    base: Handler[I, O],
    tx: TransactionManagerService,
    options: Optional[TransactionalOptions] = None,
) -> CommandTransactionalDecorator[I, O]:
    return CommandTransactionalDecorator(base, tx, options)


def NewCommandTransactionalDecorator(
    base: Handler[I, O],
    tx: TransactionManagerService,
    options: Optional[TransactionalOptions] = None,
) -> CommandTransactionalDecorator[I, O]:
    return new_command_transactional_decorator(base, tx, options)

