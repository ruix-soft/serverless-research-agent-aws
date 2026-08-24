from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable, Tuple
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.authorization_error import new_authorization_error
from context.kit.service.authorization_service import AuthorizationService

I = TypeVar("I")
O = TypeVar("O")

QueryAuthTransformFn = Callable[[I, str, Optional[Metadata]], Tuple[Any, str, Optional[Metadata]]]


@dataclass
class QueryAuthorizationOptions(Generic[I]):
    transform: Optional[QueryAuthTransformFn] = None


class QueryAuthorizationDecorator(Generic[I, O], Query[I, O]):
    """
    QueryAuthorizationDecorator envuelve una Query para verificar permisos antes de ejecutar.
    """

    def __init__(
        self,
        base: Query[I, O],
        authorizer: AuthorizationService,
        options: Optional[QueryAuthorizationOptions[I]] = None,
    ) -> None:
        self._base = base
        self._authorizer = authorizer
        self._options = options or QueryAuthorizationOptions()

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryAuthorizationDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        q_type = self.query_type()
        meta = self.metadata()

        auth_payload = payload
        auth_type = q_type
        auth_meta = meta

        if self._options.transform is not None:
            auth_payload, auth_type, auth_meta = self._options.transform(payload, q_type, meta)

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


def new_query_authorization_decorator(
    base: Query[I, O],
    authorizer: AuthorizationService,
    options: Optional[QueryAuthorizationOptions[I]] = None,
) -> QueryAuthorizationDecorator[I, O]:
    return QueryAuthorizationDecorator(base, authorizer, options)


def NewQueryAuthorizationDecorator(
    base: Query[I, O],
    authorizer: AuthorizationService,
    options: Optional[QueryAuthorizationOptions[I]] = None,
) -> QueryAuthorizationDecorator[I, O]:
    return new_query_authorization_decorator(base, authorizer, options)

