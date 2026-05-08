import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


def _fix_json(raw: str) -> str:
    """Escape unescaped control characters inside JSON string values only."""
    result = []
    in_string = False
    escaped = False
    for ch in raw:
        if escaped:
            result.append(ch)
            escaped = False
        elif ch == "\\" and in_string:
            result.append(ch)
            escaped = True
        elif ch == '"':
            in_string = not in_string
            result.append(ch)
        elif in_string and ch == "\n":
            result.append("\\n")
        elif in_string and ch == "\r":
            result.append("\\r")
        elif in_string and ch == "\t":
            result.append("\\t")
        else:
            result.append(ch)
    return "".join(result)


class JSONSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "application/json" in request.headers.get("content-type", ""):
            raw = await request.body()
            try:
                json.loads(raw)
            except json.JSONDecodeError:
                fixed = _fix_json(raw.decode("utf-8", errors="replace")).encode("utf-8")
                logger.warning("Sanitized malformed JSON body on %s", request.url.path)
                request._body = fixed

        return await call_next(request)
