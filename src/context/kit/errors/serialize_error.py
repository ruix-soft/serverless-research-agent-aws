import json
import traceback
from typing import Optional, Dict, Any


def serialize_error(err: Any) -> Optional[Dict[str, Any]]:
    """
    Convierte cualquier valor (excepción, dict u objeto arbitrario) en una estructura serializable.
    Traducción de SerializeError de Go a Python.
    """
    if err is None:
        return None

    if isinstance(err, BaseException):
        stack_str = "".join(traceback.format_exception(type(err), err, err.__traceback__)) if err.__traceback__ else ""
        cause_data = serialize_error(err.__cause__) if err.__cause__ is not None else None

        code_val = getattr(err, "code", None) or getattr(err, "err_type", None) or None

        return {
            "name": err.__class__.__name__,
            "message": str(err),
            "stack": stack_str if stack_str else None,
            "code": str(code_val) if code_val else None,
            "cause": cause_data,
        }

    if isinstance(err, (dict, list, tuple, set)):
        try:
            return {
                "name": "ObjectThrownError",
                "message": json.dumps(err, ensure_ascii=False, default=str),
                "stack": None,
                "code": None,
                "cause": None,
            }
        except Exception:
            pass

    return {
        "name": "UnknownThrownError",
        "message": str(err),
        "stack": None,
        "code": None,
        "cause": None,
    }


def SerializeError(err: Any) -> Optional[Dict[str, Any]]:
    """Alias Go-style para serialize_error."""
    return serialize_error(err)

