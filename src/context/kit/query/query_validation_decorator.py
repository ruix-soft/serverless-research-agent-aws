from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable, Tuple
from context.kit.query.query import Query
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.validation_error import new_validation_error
from context.kit.service.validation_service import ValidationService

I = TypeVar("I")
O = TypeVar("O")

QueryValidationTransformFn = Callable[[I, str, Optional[Metadata]], Tuple[Any, str, Optional[Metadata]]]


@dataclass
class QueryValidationOptions(Generic[I]):
    transform: Optional[QueryValidationTransformFn] = None


class QueryValidationDecorator(Generic[I, O], Query[I, O]):
    """
    QueryValidationDecorator envuelve una Query para validar el payload antes de ejecutar.
    """

    def __init__(
        self,
        base: Query[I, O],
        validator: ValidationService,
        options: Optional[QueryValidationOptions[I]] = None,
    ) -> None:
        self._base = base
        self._validator = validator
        self._options = options or QueryValidationOptions()

    def query_type(self) -> str:
        t = self._base.query_type()
        return t if t else "QueryValidationDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        q_type = self.query_type()
        meta = self.metadata()

        val_payload = payload
        val_type = q_type
        val_meta = meta

        if self._options.transform is not None:
            val_payload, val_type, val_meta = self._options.transform(payload, q_type, meta)

        try:
            val_result = self._validator.validate(val_payload, val_type, val_meta, ctx)
        except Exception as exc:
            infra_err = DomainError(
                err_type="validation_infrastructure_error",
                message=f"Failed to execute validation: {exc}",
            )
            return Result.err(infra_err)

        if not val_result.valid:
            msg = val_result.message if val_result.message else "Validation failed"
            val_err = new_validation_error(msg, val_result.details)
            return Result.err(val_err)

        return self._base.execute(payload, ctx)


def new_query_validation_decorator(
    base: Query[I, O],
    validator: ValidationService,
    options: Optional[QueryValidationOptions[I]] = None,
) -> QueryValidationDecorator[I, O]:
    return QueryValidationDecorator(base, validator, options)


def NewQueryValidationDecorator(
    base: Query[I, O],
    validator: ValidationService,
    options: Optional[QueryValidationOptions[I]] = None,
) -> QueryValidationDecorator[I, O]:
    return new_query_validation_decorator(base, validator, options)

