import os
import json
from typing import Optional, Any
import boto3
from botocore.exceptions import ClientError
from context.research.domain.ports import IStateMachineInvokerPort


class StepFunctionsInvokerAdapter(IStateMachineInvokerPort):
    """
    Adapter for triggering AWS Step Functions State Machine executions asynchronously.
    """

    def __init__(
        self,
        state_machine_arn: Optional[str] = None,
        sfn_client: Optional[Any] = None,
        region_name: Optional[str] = None,
    ) -> None:
        self._state_machine_arn = state_machine_arn or os.getenv(
            "STATE_MACHINE_ARN",
            "arn:aws:states:us-east-1:123456789012:stateMachine:ResearchStateMachine"
        )
        self._region = region_name or os.getenv(
            "AWS_REGION",
            os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        self._sfn_client = sfn_client or boto3.client(
            "stepfunctions",
            region_name=self._region
        )

    def start_execution(self, job_id: str, topic: str) -> None:
        """Starts asynchronous execution of the research state machine."""
        payload = {
            "job_id": job_id,
            "topic": topic
        }
        # Execution name must be unique (up to 80 characters, [a-zA-Z0-9_-])
        safe_job_id = job_id.replace(":", "-")
        execution_name = f"job-{safe_job_id}"[:80]

        try:
            self._sfn_client.start_execution(
                stateMachineArn=self._state_machine_arn,
                name=execution_name,
                input=json.dumps(payload)
            )
        except ClientError as e:
            raise RuntimeError(f"Error iniciando ejecución en Step Functions: {str(e)}") from e

