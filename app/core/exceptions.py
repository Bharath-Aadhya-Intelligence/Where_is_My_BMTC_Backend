"""Custom application exceptions with HTTP status codes."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=422)


class DatabaseException(AppException):
    def __init__(self, detail: str = "Database error"):
        super().__init__(detail=detail, status_code=500)
