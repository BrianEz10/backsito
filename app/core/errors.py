from fastapi import HTTPException


def http_error(status_code: int, detail: str, code: str, field: str | None = None) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"detail": detail, "code": code, "field": field})