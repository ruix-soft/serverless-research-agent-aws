from typing import Any, Dict
from app.aws.powertools import logger, tracer, metrics
from app.controllers.execute_research_worker_controller import ExecuteResearchWorkerController
from context.research.application.dtos.execute_research_worker_dto import ExecuteResearchWorkerInputDTO

# Module-scope assembly
_controller = ExecuteResearchWorkerController()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda Delivery Handler for Background Research Worker.
    Responsible strictly for event payload extraction, DTO creation,
    invoking the controller, and returning execution status.
    """
    job_id = event.get("job_id")
    topic = event.get("topic")

    if not job_id or not topic:
        error_msg = "Payload de evento inválido: 'job_id' y 'topic' son obligatorios."
        logger.error(error_msg, extra={"event": event})
        raise ValueError(error_msg)

    input_dto = ExecuteResearchWorkerInputDTO(job_id=job_id, topic=topic)
    result = _controller.run(input_dto)

    is_ok = result.is_ok() if callable(getattr(result, "is_ok", None)) else getattr(result, "is_ok", False)

    if is_ok:
        val = result.get() if hasattr(result, "get") else getattr(result, "value", None)
        return val.to_dict() if hasattr(val, "to_dict") else val
    else:
        err = result.get_error() if hasattr(result, "get_error") else getattr(result, "error", None)
        err_msg = getattr(err, "message", str(err))
        if hasattr(err, "to_dict"):
            err_data = err.to_dict()
        elif hasattr(err, "to_primitives"):
            err_data = err.to_primitives()
        else:
            err_data = str(err)

        logger.error(
            f"Fallo en la ejecución del worker para job_id={job_id}: {err_msg}",
            extra={"error": err_data}
        )
        raise RuntimeError(f"Error en worker: {err_msg}")
