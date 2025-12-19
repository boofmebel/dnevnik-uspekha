"""
Роутер для родителя
Согласно требованиям: родитель управляет детьми, настройками, правилами семьи
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.child import ChildCreate, ChildUpdate, ChildResponse
from schemas.settings import SettingsUpdate, SettingsResponse
from schemas.family_rules import FamilyRulesResponse, FamilyRulesUpdate
from schemas.auth import ChildAccessResponse
from repositories.child_repository import ChildRepository
from repositories.child_access_repository import ChildAccessRepository
from repositories.settings_repository import SettingsRepository
from repositories.family_rules_repository import FamilyRulesRepository
from core.database import get_db
from core.dependencies import get_current_user
from core.security.password import hash_password
from datetime import datetime, timedelta
import qrcode
import io
import base64
import json

router = APIRouter()


def check_parent_role(current_user: dict = Depends(get_current_user)) -> dict:
    """Проверка, что пользователь - родитель"""
    if current_user.get("role") != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только родителям"
        )
    return current_user


@router.get("/children", response_model=list[ChildResponse])
async def get_children(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Получение списка детей родителя"""
    repo = ChildRepository(db)
    children = await repo.get_by_user_id(current_user["id"])
    return [ChildResponse.model_validate(c) for c in children]


@router.post("/children", response_model=ChildResponse)
async def create_child(
    child_data: ChildCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Создание ребёнка"""
    repo = ChildRepository(db)
    child = await repo.create({
        **child_data.model_dump(),
        "user_id": current_user["id"]
    })
    
    # Создаём настройки по умолчанию для нового ребёнка
    settings_repo = SettingsRepository(db)
    await settings_repo.get_or_create(child.id)
    
    return ChildResponse.model_validate(child)


@router.put("/children/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    child_data: ChildUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Обновление ребёнка"""
    repo = ChildRepository(db)
    child = await repo.get_by_id(child_id)
    
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    child = await repo.update(child, child_data.model_dump(exclude_unset=True))
    return ChildResponse.model_validate(child)


@router.delete("/children/{child_id}")
async def delete_child(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Удаление ребёнка"""
    repo = ChildRepository(db)
    child = await repo.get_by_id(child_id)
    
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    await repo.delete(child)
    return {"message": "Ребёнок удалён"}


@router.get("/children/{child_id}/settings", response_model=SettingsResponse)
async def get_child_settings(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Получение настроек ребёнка"""
    child_repo = ChildRepository(db)
    settings_repo = SettingsRepository(db)
    
    # Проверяем, что ребёнок принадлежит родителю
    child = await child_repo.get_by_id(child_id)
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    settings = await settings_repo.get_or_create(child_id)
    return SettingsResponse.model_validate(settings)


@router.put("/children/{child_id}/settings", response_model=SettingsResponse)
async def update_child_settings(
    child_id: int,
    settings_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Обновление настроек ребёнка"""
    child_repo = ChildRepository(db)
    settings_repo = SettingsRepository(db)
    
    # Проверяем, что ребёнок принадлежит родителю
    child = await child_repo.get_by_id(child_id)
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    settings = await settings_repo.get_or_create(child_id)
    settings = await settings_repo.update(settings, settings_data.model_dump(exclude_unset=True))
    return SettingsResponse.model_validate(settings)


@router.post("/children/{child_id}/qr", response_model=ChildAccessResponse)
async def generate_child_qr(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Генерация QR-кода для ребёнка"""
    child_repo = ChildRepository(db)
    access_repo = ChildAccessRepository(db)
    
    # Проверяем, что ребёнок принадлежит родителю
    child = await child_repo.get_by_id(child_id)
    if not child or child.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ребёнок не найден"
        )
    
    # Проверяем, есть ли уже доступ
    existing_access = await access_repo.get_by_child_id(child_id)
    
    # Генерируем QR-токен
    qr_token = access_repo.generate_qr_token()
    qr_token_expires_at = datetime.now() + timedelta(days=30)
    
    if existing_access:
        # Обновляем существующий доступ (но не меняем PIN)
        access = await access_repo.update(existing_access, {
            "qr_token": qr_token,
            "qr_token_expires_at": qr_token_expires_at,
            "is_active": True
        })
        pin_set = access.pin_hash is not None
    else:
        # Создаём новый доступ (PIN будет установлен при первом входе по QR)
        # pin_hash = NULL до первого входа
        access = await access_repo.create({
            "child_id": child_id,
            "pin_hash": None,  # PIN не создаётся до первого входа
            "qr_token": qr_token,
            "qr_token_expires_at": qr_token_expires_at,
            "is_active": True
        })
        pin_set = False
    
    # Генерируем QR-код
    # Безопасность: QR содержит только токен, child_id определяется на сервере
    qr_data = {
        "token": qr_token
    }
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
        qr_token=qr_token,
        pin="",  # PIN не показываем при генерации QR
        pin_set=pin_set,
        expires_at=qr_token_expires_at.isoformat()
    )


@router.get("/rules", response_model=FamilyRulesResponse)
async def get_family_rules(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Получение правил семьи"""
    rules_repo = FamilyRulesRepository(db)
    rules = await rules_repo.get_or_create(current_user["id"])
    
    # Парсим правила из JSON
    rules_list = rules_repo.parse_rules(rules)
    
    return FamilyRulesResponse(
        id=rules.id,
        user_id=rules.user_id,
        rules=rules_list,
        created_at=rules.created_at,
        updated_at=rules.updated_at
    )


@router.put("/rules", response_model=FamilyRulesResponse)
async def update_family_rules(
    rules_data: FamilyRulesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_parent_role)
):
    """Обновление правил семьи"""
    rules_repo = FamilyRulesRepository(db)
    rules = await rules_repo.get_or_create(current_user["id"])
    
    # Обновляем правила
    rules = await rules_repo.update(rules, rules_data.rules)
    
    # Парсим для ответа
    rules_list = rules_repo.parse_rules(rules)
    
    return FamilyRulesResponse(
        id=rules.id,
        user_id=rules.user_id,
        rules=rules_list,
        created_at=rules.created_at,
        updated_at=rules.updated_at
    )



