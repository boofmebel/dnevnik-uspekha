"""
Кастомные исключения
Согласно rules.md: обработка ошибок, безопасность
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """Ресурс не найден"""
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message, status_code=404)


class UnauthorizedError(AppException):
    """Не авторизован"""
    def __init__(self, message: str = "Требуется авторизация"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """Доступ запрещён"""
    def __init__(self, message: str = "Доступ запрещён"):
        super().__init__(message, status_code=403)


class ValidationError(AppException):
    """Ошибка валидации"""
    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(message, status_code=400)


async def app_exception_handler(request: Request, exc: AppException):
    """Обработчик кастомных исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Ошибка валидации данных",
            "details": exc.errors()
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

