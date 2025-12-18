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
    repo = ChildRepository(db)
    child = await repo.create({
        **child_data.model_dump(),
        "user_id": current_user["id"]
    })
    return ChildResponse.model_validate(child)


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
    child_repo = ChildRepository(db)
    access_repo = ChildAccessRepository(db)
    
    # Проверяем, что ребёнок принадлежит текущему пользователю
    child = await child_repo.get_by_id(child_id)
    if not child or child.user_id != current_user["id"]:
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
    qr_token_expires_at = datetime.now() + timedelta(days=30)  # QR действует 30 дней
    
    if existing_access:
        # Обновляем существующий доступ
        access = await access_repo.update(existing_access, {
            "pin_hash": pin_hash,
            "qr_token": qr_token,
            "qr_token_expires_at": qr_token_expires_at,
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
            "is_active": True
        })
    
    # Генерируем QR-код (изображение)
    # Формат данных: JSON с токеном и информацией
    qr_data = {
        "token": qr_token,
        "child_id": child_id,
        "name": child.name
    }
    import json
    qr_data_str = json.dumps(qr_data)
    
    # Создаём QR-код
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data_str)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    qr_code_base64 = f"data:image/png;base64,{img_str}"
    
    return ChildAccessResponse(
        child_id=child_id,
        qr_code=qr_code_base64,
        qr_token=qr_token,
        pin=pin,  # Показываем только один раз при генерации
        pin_set=True,
        expires_at=qr_token_expires_at.isoformat()
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
