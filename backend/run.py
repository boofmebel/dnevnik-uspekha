#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI приложения
Использование: python run.py
"""
import uvicorn
from core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

