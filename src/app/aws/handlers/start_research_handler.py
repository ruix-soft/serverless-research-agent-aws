import json
from typing import Any, Dict
from app.aws.powertools import logger, tracer, metrics
from app.aws.response import build_api_response, map_result_to_api_response
from app.controllers.start_research_controller import StartResearchController
from context.research.application.dtos.start_research_dto import StartResearchInputDTO

# Module-scope assembly
_controller = StartResearchController()

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda Delivery Handler for POST /research
    Responsible strictly for event parsing, DTO creation, invoking the controller,
    and mapping the Result to an HTTP response.
    """
    try:
        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except Exception as e:
        logger.warning(f"Malformed JSON payload received: {str(e)}")
        return build_api_response(
            status_code=400,
            body={"code": "BAD_REQUEST", "message": "El cuerpo de la petición no es un JSON válido."}
        )

    topic = body.get("topic")
    if not topic:
        return build_api_response(
            status_code=400,
            body={"code": "VALIDATION_ERROR", "message": "El campo 'topic' es obligatorio."}
        )

    input_dto = StartResearchInputDTO(
        topic=topic,
        depth=body.get("depth", "detailed"),
        format=body.get("format", "markdown"),
        search_limit=body.get("search_limit", 5)
    )

    result = _controller.run(input_dto)
    return map_result_to_api_response(result, success_status_code=202)

