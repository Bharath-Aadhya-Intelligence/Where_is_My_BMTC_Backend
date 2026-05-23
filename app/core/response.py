"""Standardized API response helpers."""

from typing import Any

from fastapi.responses import JSONResponse


def api_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "message": message},
    )


def error_response(
    detail: str,
    status_code: int = 400,
    message: str | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": detail,
            "message": message or detail,
        },
    )
