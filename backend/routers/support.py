"""
Роутер для поддержки и жалоб
Согласно требованиям: логирование жалоб через Notification
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.notification import ComplaintRequest
from services.notification_service import NotificationService
from models.notification import NotificationType
from core.database import get_db
from core.dependencies import get_current_user, check_parent_consent

router = APIRouter()


@router.post("/complaint")
async def create_complaint(
    complaint_data: ComplaintRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(check_parent_consent)
):
    """
    Отправка жалобы
    Согласно требованиям: проверка согласия родителей и логирование
    """
    if not complaint_data.parent_consent:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется подтверждение согласия родителя на обработку жалобы"
        )
    
    # Получаем IP и User-Agent для аудита
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Логируем жалобу
    notification_service = NotificationService(db)
    result = await notification_service.send_notification(
        user_id=current_user["id"],
        type=NotificationType.COMPLAINT,
        message=f"Жалоба: {complaint_data.subject}\n\n{complaint_data.message}",
        metadata={
            "subject": complaint_data.subject,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    )
    
    return {
        "status": "success",
        "message": "Жалоба успешно отправлена. Мы рассмотрим её в ближайшее время.",
        "complaint_id": result["id"]
    }

