"""
Pydantic схемы для юридических текстов
Согласно требованиям: простые тексты с юридическими аспектами РФ
"""
from pydantic import BaseModel


class LegalTextResponse(BaseModel):
    """Схема ответа с юридическим текстом"""
    title: str
    content: str
    last_updated: str
    version: str

