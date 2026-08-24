from typing import Any, Dict
from app.aws.powertools import logger, tracer, metrics
from app.aws.response import build_api_response, map_result_to_api_response
from app.controllers.get_research_status_controller import GetResearchStatusController
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
    result = _controller.run(input_dto)
    return map_result_to_api_response(result, success_status_code=200)

