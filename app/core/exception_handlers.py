import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    content = (
        exc.detail
        if isinstance(exc.detail, dict)
        else {"detail": exc.detail, "code": "HTTP_ERROR", "field": None}
    )
    logger.warning(
        "[%s] %s → HTTP %d: %s",
        request.method,
        request.url.path,
        exc.status_code,
        content,
    )
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    first = errors[0] if errors else {}
    content = {
        "detail": first.get("msg", "Error de validación"),
        "code": "VALIDATION_ERROR",
        "field": ".".join(str(loc) for loc in first.get("loc", [])),
    }
    logger.warning("[%s] %s → 422: %s", request.method, request.url.path, errors)
    return JSONResponse(status_code=422, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("💥 Error no manejado en [%s] %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "code": "INTERNAL_ERROR", "field": None},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
