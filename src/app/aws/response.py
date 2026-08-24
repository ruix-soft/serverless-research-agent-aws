import json
from typing import Any, Dict, Optional
from context.kit.dtos.result import Result
from context.kit.errors.domain_error import DomainError

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
}


def build_api_response(
    status_code: int,
    body: Any,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Constructs a standard API Gateway REST response format."""
    response_headers = {**DEFAULT_HEADERS, **(headers or {})}
    serialized_body = json.dumps(body) if not isinstance(body, str) else body

    return {
        "statusCode": status_code,
        "headers": response_headers,
        "body": serialized_body
    }


def map_error_to_status_code(error: Any) -> int:
    """Maps a DomainError to an appropriate HTTP status code."""
    err_type = (
        getattr(error, "err_type", "")
        or getattr(error, "type", "")
        or getattr(error, "code", "")
        or ""
    ).lower()

    if "validation" in err_type or err_type == "bad_request":
        return 400
    if "not_found" in err_type:
        return 404
    if "authorization" in err_type or "forbidden" in err_type:
        return 403
    if "rate_limit" in err_type:
        return 429
    if "conflict" in err_type:
        return 409
    if "infrastructure" in err_type:
        return 502
    return 500


def map_result_to_api_response(
    result: Any,
    success_status_code: int = 200
) -> Dict[str, Any]:
    """Maps a Result object to an API Gateway response."""
    is_ok = result.is_ok() if callable(getattr(result, "is_ok", None)) else getattr(result, "is_ok", False)

    if is_ok:
        value = result.get() if hasattr(result, "get") else getattr(result, "value", None)
        body = value.to_dict() if hasattr(value, "to_dict") else value
        return build_api_response(status_code=success_status_code, body=body)

    error = result.get_error() if hasattr(result, "get_error") else getattr(result, "error", None)
    status_code = map_error_to_status_code(error)
    if hasattr(error, "to_dict"):
        error_body = error.to_dict()
    elif hasattr(error, "to_primitives"):
        error_body = error.to_primitives()
    else:
        error_body = {"message": str(error)}

    return build_api_response(status_code=status_code, body=error_body)
