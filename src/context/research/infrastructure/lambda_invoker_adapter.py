import os
import json
import boto3
from botocore.exceptions import ClientError
from context.research.domain.ports import IAsyncWorkerInvokerPort

class LambdaInvokerAdapter(IAsyncWorkerInvokerPort):
    """Adapter to asynchronously invoke the research worker Lambda."""
    def __init__(self, lambda_client=None, function_name: str = None):
        self._region = os.getenv("AWS_REGION", "mx-central-1")
        self._lambda_client = lambda_client or boto3.client("lambda", region_name=self._region)
        self._function_name = (
            function_name
            or os.getenv("WORKER_FUNCTION_NAME")
            or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        )

    def invoke_worker(self, job_id: str, topic: str) -> None:
        if not self._function_name:
            raise RuntimeError("No se especificó el nombre de la función Lambda worker.")

        payload = {
            "source": "async_worker",
            "job_id": job_id,
            "topic": topic
        }

        try:
            self._lambda_client.invoke(
                FunctionName=self._function_name,
                InvocationType="Event",
                Payload=json.dumps(payload)
            )
        except ClientError as e:
            raise RuntimeError(f"Error invocando la función Lambda asíncrona: {str(e)}")

