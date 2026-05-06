"""Custom exception classes for the application."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class StockNotFoundException(NotFoundException):
    """Stock ticker not found exception."""

    def __init__(self, ticker: str):
        super().__init__(f"Stock '{ticker}' not found")


class ValidationException(AppException):
    """Input validation exception."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)


class TickerValidationException(ValidationException):
    """Invalid ticker format exception."""

    def __init__(self, ticker: str):
        super().__init__(f"Invalid ticker format: '{ticker}'. Must end with .JK")


class DataImportException(AppException):
    """Data import failure exception."""

    def __init__(self, message: str = "Failed to import data"):
        super().__init__(message, status_code=502)


class ConflictException(AppException):
    """Data conflict exception."""

    def __init__(self, message: str = "Data conflict"):
        super().__init__(message, status_code=409)


class BacktestException(AppException):
    """Backtest execution exception."""

    def __init__(self, message: str = "Backtest failed"):
        super().__init__(message, status_code=500)
