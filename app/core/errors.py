class AppError(Exception):
    def __init__(self, message: str = "Application error"):
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service error"):
        super().__init__(message)
