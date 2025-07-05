from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.models import Notification, User
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from app.session import get_session
from app.utils.user import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post(
    "/",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createNotification"
)
def create_notification(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    notification_in: NotificationCreate
):
    notification = Notification(
        **notification_in.model_dump(exclude_unset=True),
        user_id=current_user.id  # Asignar automáticamente
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@router.get(
    "/",
    response_model=List[NotificationRead],
    operation_id="listNotifications"
)
def list_notifications(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    notifications = session.exec(query).all()
    return notifications

@router.get(
    "/{notification_id}",
    response_model=NotificationRead,
    operation_id="getNotification"
)
def get_notification(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    notification_id: int
):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put(
    "/{notification_id}",
    response_model=NotificationRead,
    operation_id="updateNotification"
)
def update_notification(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    notification_id: int,
    notification_in: NotificationUpdate
):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in notification_in.model_dump(exclude_unset=True).items():
        setattr(notification, key, value)

    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteNotification"
)
def delete_notification(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    notification_id: int
):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    session.delete(notification)
    session.commit()