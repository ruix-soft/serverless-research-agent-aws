from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any, Callable, Tuple
from context.kit.command.command import Handler
from context.kit.dtos.metadata import Metadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError
from context.kit.errors.validation_error import new_validation_error
from context.kit.service.validation_service import ValidationService

I = TypeVar("I")
O = TypeVar("O")

ValidationTransformFn = Callable[[I, str, Optional[Metadata]], Tuple[Any, str, Optional[Metadata]]]


@dataclass
class ValidationOptions(Generic[I]):
    transform: Optional[ValidationTransformFn] = None


class CommandValidationDecorator(Generic[I, O], Handler[I, O]):
    """
    CommandValidationDecorator envuelve un Command para validar el payload antes de ejecutar.
    """

    def __init__(
        self,
        base: Handler[I, O],
        validator: ValidationService,
        options: Optional[ValidationOptions[I]] = None,
    ) -> None:
        self._base = base
        self._validator = validator
        self._options = options or ValidationOptions()

    def command_type(self) -> str:
        t = self._base.command_type()
        return t if t else "CommandValidationDecorator"

    def metadata(self) -> Optional[Metadata]:
        return self._base.metadata()

    def execute(self, payload: I, ctx: Optional[Any] = None) -> Result[O, DomainError]:
        cmd_type = self.command_type()
        meta = self.metadata()

        val_payload = payload
        val_type = cmd_type
        val_meta = meta

        if self._options.transform is not None:
            val_payload, val_type, val_meta = self._options.transform(payload, cmd_type, meta)

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


def new_command_validation_decorator(
    base: Handler[I, O],
    validator: ValidationService,
    options: Optional[ValidationOptions[I]] = None,
) -> CommandValidationDecorator[I, O]:
    return CommandValidationDecorator(base, validator, options)


def NewCommandValidationDecorator(
    base: Handler[I, O],
    validator: ValidationService,
    options: Optional[ValidationOptions[I]] = None,
) -> CommandValidationDecorator[I, O]:
    return new_command_validation_decorator(base, validator, options)

