"""
JWT токены
Согласно rules.md: Access token 5-15 минут, Refresh token в HttpOnly cookie
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from core.config import settings
import time


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access token (согласно rules.md: 5-15 минут)"""
    to_encode = data.copy()
    # Используем time.time() для правильного UTC timestamp
    current_timestamp = int(time.time())
    if expires_delta:
        expire_timestamp = current_timestamp + int(expires_delta.total_seconds())
    else:
        expire_timestamp = current_timestamp + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    # Используем timestamp для надежности
    to_encode.update({"exp": expire_timestamp, "type": "access"})
    
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in settings!")
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh token (согласно rules.md: HttpOnly cookie)"""
    to_encode = data.copy()
    # Используем time.time() для правильного UTC timestamp
    current_timestamp = int(time.time())
    expire_timestamp = current_timestamp + (settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    # Используем timestamp для надежности
    to_encode.update({"exp": expire_timestamp, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Проверка токена"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем наличие SECRET_KEY
        if not settings.SECRET_KEY:
            logger.error("SECRET_KEY is not set!")
            return None
        
        logger.info(f"Verifying token: length={len(token)}, SECRET_KEY length={len(settings.SECRET_KEY)}, algorithm={settings.ALGORITHM}")
        
        # Пробуем декодировать без проверки подписи для диагностики (только для отладки!)
        try:
            # В python-jose нужно передать ключ, даже если не проверяем подпись
            unverified = jwt.decode(token, key="", options={"verify_signature": False, "verify_exp": False})
            logger.info(f"Token structure (unverified): {unverified}")
            exp_timestamp = unverified.get('exp')
            current_timestamp = int(time.time())  # Используем time.time() для правильного UTC timestamp
            logger.info(f"Token exp: {exp_timestamp}, current time: {current_timestamp}")
            if exp_timestamp:
                time_until_expiry = exp_timestamp - current_timestamp
                logger.info(f"Token expires in: {time_until_expiry:.0f} seconds ({time_until_expiry/60:.1f} minutes)")
                if time_until_expiry < 0:
                    logger.warning("⚠️ Token is EXPIRED!")
        except Exception as e:
            logger.warning(f"Could not decode token structure: {e}")
        
        # Декодируем с проверкой подписи
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            logger.info(f"✅ Token decoded successfully with signature verification. Payload: {payload}")
        except Exception as e:
            logger.error(f"❌ Error decoding token: {type(e).__name__}: {e}")
            raise
        
        token_type_in_payload = payload.get("type")
        # Разрешаем токены без типа для обратной совместимости (старые токены)
        if token_type_in_payload is None:
            logger.warning("Token has no type field, allowing for backward compatibility")
            return payload
        
        if token_type_in_payload != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {token_type_in_payload}")
            return None
        
        logger.info(f"Token type verified: {token_type}")
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"Token expired: {e}")
        return None
    except JWTError as e:
        # JWTError включает все ошибки JWT, включая проблемы с подписью
        error_msg = str(e)
        if "signature" in error_msg.lower() or "invalid" in error_msg.lower():
            logger.error(f"Invalid token signature - SECRET_KEY mismatch: {e}")
        else:
            logger.warning(f"JWT Error: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {type(e).__name__}: {e}", exc_info=True)
        return None

