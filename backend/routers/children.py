"""
Роутер для работы с детьми
Согласно rules.md: thin controllers (только вызовы сервисов)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.child import ChildCreate, ChildUpdate, ChildResponse
from schemas.auth import ChildAccessResponse
from repositories.child_repository import ChildRepository
from repositories.child_access_repository import ChildAccessRepository
from core.database import get_db
from core.dependencies import get_current_user
from core.security.password import hash_password
from datetime import datetime, timedelta
import qrcode
import io
import base64

router = APIRouter()


@router.get("/", response_model=list[ChildResponse])
async def get_children(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение списка детей пользователя"""
    repo = ChildRepository(db)
    children = await repo.get_by_user_id(current_user["id"])
    return [ChildResponse.model_validate(c) for c in children]


@router.post("/", response_model=ChildResponse)
async def create_child(
    child_data: ChildCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание ребёнка"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        repo = ChildRepository(db)
        logger.info(f"Создание ребенка для user_id={current_user['id']}, данные: {child_data.model_dump()}")
        
        # Подготавливаем данные для создания
        from models.child import Gender
        
        # Получаем данные из Pydantic модели
        # Pydantic конвертирует строку в Gender enum при валидации
        child_dict = child_data.model_dump(exclude_unset=True)
        
        # КРИТИЧЕСКИ ВАЖНО: Конвертируем Gender enum в строку (значение enum) для SQLAlchemy
        # SQLAlchemy с native_enum=False ожидает строку, а не enum объект
        if 'gender' in child_dict:
            gender_value = child_dict['gender']
            # Если это Gender enum, берем его значение (строку)
            if isinstance(gender_value, Gender):
                child_dict['gender'] = gender_value.value
            # Если это уже строка, оставляем как есть
            elif not isinstance(gender_value, str):
                # Если это что-то другое, пытаемся преобразовать
                if hasattr(gender_value, 'value'):
                    child_dict['gender'] = gender_value.value
                else:
                    child_dict['gender'] = str(gender_value)
        
        logger.info(f"Создание ребенка с данными: {child_dict}")
        
        child = await repo.create({
            **child_dict,
            "user_id": current_user["id"]
        })
        
        # Убеждаемся, что ID получен
        await db.flush()
        await db.refresh(child)
        
        logger.info(f"Ребенок создан успешно: id={child.id}, name={child.name}")
        
        return ChildResponse.model_validate(child)
    except Exception as e:
        logger.error(f"Ошибка создания ребенка: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания ребенка: {str(e)}"
        )


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    child_data: ChildUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновление ребёнка"""
    repo = ChildRepository(db)
    child = await repo.get_by_id(child_id)
    
    if not child or child.user_id != current_user["id"]:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    child = await repo.update(child, child_data.model_dump(exclude_unset=True))
    return ChildResponse.model_validate(child)


@router.delete("/{child_id}")
async def delete_child(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удаление ребёнка"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        repo = ChildRepository(db)
        child = await repo.get_by_id(child_id)
        
        if not child or child.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ребёнок не найден"
            )
        
        # Удаляем связанные данные (access, tasks, stars и т.д.)
        # SQLAlchemy должен обработать каскадное удаление, но лучше сделать явно
        access_repo = ChildAccessRepository(db)
        access = await access_repo.get_by_child_id(child_id)
        if access:
            await access_repo.delete(access)
        
        # Удаляем ребенка
        await repo.delete(child)
        await db.commit()
        
        logger.info(f"Ребенок удален: id={child_id}, user_id={current_user['id']}")
        
        return {"message": "Ребёнок успешно удалён"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления ребенка {child_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления ребёнка: {str(e)}"
        )


@router.post("/{child_id}/generate-access", response_model=ChildAccessResponse)
async def generate_child_access(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Генерация QR-кода и PIN для доступа ребёнка
    Родитель может создать доступ для каждого ребёнка отдельно
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        child_repo = ChildRepository(db)
        access_repo = ChildAccessRepository(db)
        
        # Проверяем, что ребёнок принадлежит текущему пользователю
        child = await child_repo.get_by_id(child_id)
        if not child or child.user_id != current_user["id"]:
            logger.warning(f"Попытка генерации QR для чужого ребенка: child_id={child_id}, user_id={current_user['id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ребёнок не найден"
            )
        
        # Проверяем, есть ли уже доступ
        existing_access = await access_repo.get_by_child_id(child_id)
        
        # Генерируем PIN (4 цифры)
        pin = access_repo.generate_pin()
        pin_hash = hash_password(pin)
        
        # Генерируем QR-токен
        qr_token = access_repo.generate_qr_token()
        now = datetime.now()
        qr_token_expires_at = now + timedelta(days=30)  # Общий срок действия: 30 дней
        qr_token_valid_from = now  # Время начала действия (для временного окна 1 час)
        qr_token_used_at = None  # Одноразовое использование: пока не использован
        
        if existing_access:
            # Обновляем существующий доступ
            access = await access_repo.update(existing_access, {
                "pin_hash": pin_hash,
                "qr_token": qr_token,
                "qr_token_expires_at": qr_token_expires_at,
                "qr_token_valid_from": qr_token_valid_from,
                "qr_token_used_at": qr_token_used_at,  # Сбрасываем при генерации нового токена
                "is_active": True,
                "failed_attempts": 0,
                "locked_until": None
            })
        else:
            # Создаём новый доступ
            access = await access_repo.create({
                "child_id": child_id,
                "pin_hash": pin_hash,
                "qr_token": qr_token,
                "qr_token_expires_at": qr_token_expires_at,
                "qr_token_valid_from": qr_token_valid_from,
                "qr_token_used_at": qr_token_used_at,
                "is_active": True
            })
        
        # Генерируем QR-код (изображение)
        # Формат данных: URL для входа ребенка с ограниченным доступом
        from core.config import settings
        frontend_url = settings.FRONTEND_URL
        qr_url = f"{frontend_url}/child?qr_token={qr_token}"
        qr_data_str = qr_url
        
        # Логируем URL для отладки
        logger.info(f"🔍 Генерация QR-кода: frontend_url={frontend_url}, qr_url={qr_url}")
        print(f"🔍 DEBUG QR: frontend_url={frontend_url}, qr_url={qr_url}")
        
        # Создаём QR-код
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data_str)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Конвертируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            qr_code_base64 = f"data:image/png;base64,{img_str}"
        except Exception as qr_error:
            logger.error(f"Ошибка генерации QR-кода: {qr_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка генерации QR-кода: {str(qr_error)}"
            )
        
        return ChildAccessResponse(
            child_id=child_id,
            qr_code=qr_code_base64,
            qr_token=qr_token,
            pin=pin,  # Показываем только один раз при генерации
            pin_set=True,
            expires_at=qr_token_expires_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при генерации доступа для ребенка {child_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/{child_id}/access", response_model=ChildAccessResponse)
async def get_child_access(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получение информации о доступе ребёнка (без PIN)
    """
    child_repo = ChildRepository(db)
    access_repo = ChildAccessRepository(db)
    
    # Проверяем, что ребёнок принадлежит текущему пользователю
    child = await child_repo.get_by_id(child_id)
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    access = await access_repo.get_by_child_id(child_id)
    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доступ для ребёнка не настроен"
        )
    
    # Генерируем QR-код заново (если нужно)
    qr_data = {
        "token": access.qr_token,
        "child_id": child_id,
        "name": child.name
    }
    import json
    qr_data_str = json.dumps(qr_data)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    qr_code_base64 = f"data:image/png;base64,{img_str}"
    
    return ChildAccessResponse(
        child_id=child_id,
        qr_code=qr_code_base64,
        qr_token=access.qr_token,
        pin="****",  # PIN не показываем
        pin_set=True,
        expires_at=access.qr_token_expires_at.isoformat() if access.qr_token_expires_at else None
    )
