from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable, Tuple
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.authorization_error import new_authorization_error
from context.kit.service.authorization_service import AuthorizationService

I = TypeVar("I")
O = TypeVar("O")

AuthTransformFn = Callable[[I, str, Optional[Metadata]], Tuple[Any, str, Optional[Metadata]]]


@dataclass
class CommandAuthorizationOptions(Generic[I]):
    transform: Optional[AuthTransformFn] = None


class CommandAuthorizationDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandAuthorizationDecorator envuelve un Command para verificar permisos antes de ejecutar.
    """

    def __init__(
        self,
        base: Handler[I, O],
        authorizer: AuthorizationService,
        options: Optional[CommandAuthorizationOptions[I]] = None,
    ) -> None:
        self._base = base
        self._authorizer = authorizer
        self._options = options or CommandAuthorizationOptions()

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandAuthorizationDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        cmd_type = self.command_type()
        meta = self.metadata()

        auth_payload = payload
        auth_type = cmd_type
        auth_meta = meta

        if self._options.transform is not None:
            auth_payload, auth_type, auth_meta = self._options.transform(payload, cmd_type, meta)

        try:
            decision = self._authorizer.authorize(auth_payload, auth_type, auth_meta, ctx)
        except Exception as exc:
            infra_err = DomainError(
                err_type="authorization_infrastructure_error",
                message=f"Failed to check authorization: {exc}",
            )
            return Result.err(infra_err)

        if not decision.authorized:
            msg = decision.reason if decision.reason else "Not authorized"
            auth_err = new_authorization_error(
                message=msg,
                status=decision.status or 403,
                reason=decision.reason or "",
            )
            return Result.err(auth_err)

        return self._base.execute(payload, ctx)


def new_command_authorization_decorator(
    base: Handler[I, O],
    authorizer: AuthorizationService,
    options: Optional[CommandAuthorizationOptions[I]] = None,
) -> CommandAuthorizationDecorator[I, O]:
    return CommandAuthorizationDecorator(base, authorizer, options)


def NewCommandAuthorizationDecorator(
    base: Handler[I, O],
    authorizer: AuthorizationService,
    options: Optional[CommandAuthorizationOptions[I]] = None,
) -> CommandAuthorizationDecorator[I, O]:
    return new_command_authorization_decorator(base, authorizer, options)

