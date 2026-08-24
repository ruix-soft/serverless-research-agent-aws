from typing import Any, Dict
from app.aws.powertools import logger, tracer, metrics
from app.aws.response import build_api_response, map_result_to_api_response
from app.controllers.get_research_status_controller import GetResearchStatusController
from context.kit.dtos.metadata import Metadata
from context.research.application.dtos.get_research_status_dto import GetResearchStatusInputDTO

# Module-scope assembly
_controller = GetResearchStatusController()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda Delivery Handler for GET /research/{job_id}
    Responsible strictly for event parsing, DTO creation, invoking the controller,
    and mapping the Result to an HTTP response.
    """
    path_parameters = event.get("pathParameters") or {}
    job_id = path_parameters.get("job_id")

    if not job_id:
        return build_api_response(
            status_code=400,
            body={"code": "VALIDATION_ERROR", "message": "El parámetro 'job_id' es obligatorio en la ruta."}
        )

    input_dto = GetResearchStatusInputDTO(job_id=job_id)

    request_context = event.get("requestContext") or {}
    identity = request_context.get("identity") or {}
    headers = event.get("headers") or {}
    client_ip = identity.get("sourceIp") or headers.get("X-Forwarded-For") or "unknown"
    user_agent = headers.get("User-Agent") or ""
    correlation_id = request_context.get("requestId") or ""

    metadata = Metadata(
        user=client_ip,
        ip=client_ip,
        user_agent=user_agent,
        correlation_id=correlation_id
    )

    result = _controller.run(input_dto, ctx=metadata)
    return map_result_to_api_response(result, success_status_code=200)
