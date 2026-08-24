import sys
import os
import json
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.research.infrastructure.step_functions_invoker_adapter import StepFunctionsInvokerAdapter


def test_step_functions_invoker_success():
    mock_client = MagicMock()
    mock_client.start_execution.return_value = {
        "executionArn": "arn:aws:states:us-east-1:123456789012:execution:ResearchStateMachine:job-123",
        "startDate": "2026-08-24T14:00:00Z"
    }

    adapter = StepFunctionsInvokerAdapter(
        state_machine_arn="arn:aws:states:us-east-1:123456789012:stateMachine:ResearchStateMachine",
        sfn_client=mock_client
    )

    adapter.start_execution(job_id="job-123", topic="Serverless Architecture")

    mock_client.start_execution.assert_called_once()
    call_kwargs = mock_client.start_execution.call_args[1]
    assert call_kwargs["stateMachineArn"] == "arn:aws:states:us-east-1:123456789012:stateMachine:ResearchStateMachine"
    assert "job-123" in call_kwargs["name"]
    payload = json.loads(call_kwargs["input"])
    assert payload["job_id"] == "job-123"
    assert payload["topic"] == "Serverless Architecture"


def test_step_functions_invoker_client_error():
    mock_client = MagicMock()
    mock_client.start_execution.side_effect = ClientError(
        error_response={"Error": {"Code": "StateMachineDoesNotExist", "Message": "Not found"}},
        operation_name="StartExecution"
    )

    adapter = StepFunctionsInvokerAdapter(
        state_machine_arn="invalid-arn",
        sfn_client=mock_client
    )

    with pytest.raises(RuntimeError, match="Error iniciando ejecución en Step Functions"):
        adapter.start_execution(job_id="job-999", topic="AI")

