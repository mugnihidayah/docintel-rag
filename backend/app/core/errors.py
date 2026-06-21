class AppError(Exception):
    """Base class for expected domain errors"""

    status_code: int = 500
    code: str = "internal error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or "Internal Server Error"
        super().__init__(self.detail)


class ValidationError(AppError):
    status_code = 400
    code = "validation_error"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class PayloadTooLargeError(AppError):
    status_code = 413
    code = "payload_too_large"


class UnsupportedFormatError(AppError):
    status_code = 415
    code = "unsupported_format"


class RateLimitedError(AppError):
    status_code = 429
    code = "rate_limited"
