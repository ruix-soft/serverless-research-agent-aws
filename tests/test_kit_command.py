import sys
import os
from typing import Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.command.command import (
    Handler,
    CommandHandler,
    BaseHandler,
    BaseCommand,
    NewBaseCommand,
    new_base_command,
)
from context.kit.dtos.metadata import Metadata, NewMetadata
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError, NewDomainError


def test_base_command_creation():
    meta = NewMetadata(user="admin", correlation_id="cid_123")
    base = NewBaseCommand("create_user", meta)

    assert base.command_type() == "create_user"
    assert base.Type() == "create_user"
    assert base.metadata() == meta
    assert base.Metadata() == meta


def test_command_handler_implementation():
    class CreateUserInput:
        def __init__(self, username: str):
            self.username = username

    class CreateUserOutput:
        def __init__(self, user_id: str):
            self.user_id = user_id

    class CreateUserHandler(Handler[CreateUserInput, CreateUserOutput], BaseHandler):
        def __init__(self, metadata: Metadata):
            BaseHandler.__init__(self, cmd_type="create_user_command", metadata=metadata)

        def execute(self, payload: CreateUserInput, ctx: Optional[Any] = None) -> Result[CreateUserOutput, DomainError]:
            if not payload.username:
                return Result.err(NewDomainError("validation_error", "Username cannot be empty", None))
            return Result.ok(CreateUserOutput(user_id=f"id_{payload.username}"))

    meta = NewMetadata(user="root")
    handler = CreateUserHandler(meta)

    assert handler.command_type() == "create_user_command"
    assert handler.Type() == "create_user_command"
    assert handler.metadata() == meta

    # Test execute success
    res = handler.execute(CreateUserInput("john_doe"))
    assert res.is_ok() is True
    assert res.get().user_id == "id_john_doe"

    # Test handle() alias
    res_handle = handler.handle(CreateUserInput("jane_doe"))
    assert res_handle.is_ok() is True
    assert res_handle.get().user_id == "id_jane_doe"

    # Test Go-style Execute(ctx, payload)
    res_go = handler.Execute(None, CreateUserInput("alice"))
    assert res_go.is_ok() is True
    assert res_go.get().user_id == "id_alice"

    # Test validation error failure
    res_err = handler.execute(CreateUserInput(""))
    assert res_err.is_error() is True
    assert res_err.get_error().err_type == "validation_error"

