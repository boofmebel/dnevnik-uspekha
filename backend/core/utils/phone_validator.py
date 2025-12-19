"""
Валидация и форматирование номеров телефонов
Согласно требованиям: регистрация по номеру телефона
"""
import re
from typing import Optional


def normalize_phone(phone: str) -> str:
    """
    Нормализация номера телефона к формату +7XXXXXXXXXX
    Удаляет все пробелы, дефисы, скобки и другие символы
    """
    # Удаляем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Если номер начинается с 8, заменяем на +7
    if cleaned.startswith('8'):
        cleaned = '+7' + cleaned[1:]
    
    # Если номер начинается с 7, добавляем +
    if cleaned.startswith('7') and not cleaned.startswith('+7'):
        cleaned = '+' + cleaned
    
    # Если номер не начинается с +, добавляем +7
    if not cleaned.startswith('+'):
        cleaned = '+7' + cleaned
    
    return cleaned


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    Проверяет формат +7XXXXXXXXXX (11 цифр после +7)
    """
    normalized = normalize_phone(phone)
    
    # Проверяем формат +7XXXXXXXXXX (всего 12 символов: +7 и 10 цифр)
    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, normalized))


def format_phone_display(phone: str) -> str:
    """
    Форматирование номера телефона для отображения
    Формат: +7 (XXX) XXX-XX-XX
    """
    normalized = normalize_phone(phone)
    
    if not validate_phone(normalized):
        return phone  # Возвращаем как есть, если невалидный
    
    # Извлекаем цифры после +7
    digits = normalized[2:]
    
    # Форматируем: +7 (XXX) XXX-XX-XX
    return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"

