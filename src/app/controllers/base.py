from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any
from context.kit.command.command import Handler, BaseHandler
from context.kit.query.query import Query, BaseQuery
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class IHandler(Generic[InputDTO, OutputDTO], ABC):
    """Base interface for Command and Query handlers."""

    @abstractmethod
    def handle(self, input_dto: InputDTO, ctx: Optional[Any] = None) -> Result[OutputDTO, DomainError]:
        pass

    def execute(self, payload: InputDTO, ctx: Optional[Any] = None) -> Result[OutputDTO, DomainError]:
        return self.handle(payload, ctx)


class ICommandHandler(IHandler[InputDTO, OutputDTO], Handler[InputDTO, OutputDTO], BaseHandler, ABC):
    """Behavioral wrapper for Command Use Cases (state mutations)."""

    def __init__(self, command_type: str = "CommandHandler"):
        BaseHandler.__init__(self, command_type=command_type)


class IQueryHandler(IHandler[InputDTO, OutputDTO], Query[InputDTO, OutputDTO], BaseQuery, ABC):
    """Behavioral wrapper for Query Use Cases (read operations)."""

    def __init__(self, query_type: str = "QueryHandler"):
        BaseQuery.__init__(self, query_type=query_type)


class BaseController(Generic[InputDTO, OutputDTO], ABC):
    """Base controller orchestrating handler execution."""

    def __init__(self, handler: Any):
        self._handler = handler

    def run(self, input_dto: InputDTO, ctx: Optional[Any] = None) -> Result[OutputDTO, DomainError]:
        if hasattr(self._handler, "handle"):
            try:
                return self._handler.handle(input_dto, ctx)
            except TypeError:
                return self._handler.handle(input_dto)
        return self._handler.execute(input_dto, ctx)
