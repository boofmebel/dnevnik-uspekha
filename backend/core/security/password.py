"""
Работа с паролями
Используем прямой bcrypt вместо passlib для избежания проблем с инициализацией
"""
import bcrypt


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    # Ограничиваем длину пароля до 72 байт (ограничение bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        # Ограничиваем длину пароля до 72 байт
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False




