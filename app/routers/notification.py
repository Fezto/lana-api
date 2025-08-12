# app/routers/notification.py (reemplazar la cabecera de imports)
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from datetime import date, datetime, timedelta

from app.models import Notification, User, RecurringPayment, Transaction, Budget
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate
from app.session import get_session
from app.utils.user import get_current_user
from app.enums.notification_method import NotificationMethod
from app.utils.email import _send_mailgun_email


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
    
    # app/routers/notification.py  -> append: comprobación de pagos próximos
@router.post("/run-checks", status_code=status.HTTP_200_OK, operation_id="runNotificationChecks")
def run_notification_checks(
    *,
    session: Session = Depends(get_session),
    background_tasks: BackgroundTasks,
    days_ahead: int = 2
):
    """
    Endpoint para ejecutar manualmente la comprobación de pagos recurrentes
    y enviar alertas si falta presupuesto. (Útil para pruebas; en producción
    conviene programarlo diariamente).
    """
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    # obtener pagos recurrentes cuyo next_due_date esté dentro de los próximos `days_ahead` días
    rps = session.exec(
        select(RecurringPayment).where(RecurringPayment.next_due_date <= cutoff)
    ).all()

    created_notifications = 0
    for rp in rps:
        user = session.get(User, rp.user_id)
        if not user:
            continue

        month_year = f"{rp.next_due_date.year}-{rp.next_due_date.month:02d}"

        # buscar presupuesto para ese mes/categoría
        budget = session.exec(
            select(Budget).where(
                Budget.user_id == user.id,
                Budget.category_id == rp.category_id,
                Budget.month_year == month_year
            )
        ).first()

        # calcular gastado en el mes
        start_date = date(rp.next_due_date.year, rp.next_due_date.month, 1)
        if rp.next_due_date.month == 12:
            next_month = date(rp.next_due_date.year + 1, 1, 1)
        else:
            next_month = date(rp.next_due_date.year, rp.next_due_date.month + 1, 1)

        txs = session.exec(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.category_id == rp.category_id,
                Transaction.date >= start_date,
                Transaction.date < next_month
            )
        ).all()
        spent = sum(t.amount for t in txs)
        remaining = (budget.amount - spent) if budget else 0.0

        # si no hay suficiente presupuesto para el pago rp.amount -> crear notificación y enviar
        if remaining < rp.amount:
            message = (
                f"Pago recurrente programado el {rp.next_due_date} por {rp.amount:.2f} "
                f"en la categoría (id={rp.category_id}). Presupuesto disponible: {remaining:.2f}."
            )
            # evitar duplicados: buscar notificación igual no enviada
            existing = session.exec(
                select(Notification).where(
                    Notification.user_id == user.id,
                    Notification.message == message,
                    Notification.sent == False
                )
            ).first()

            if existing:
                continue

            notif = Notification(
                user_id=user.id,
                message=message,
                method=NotificationMethod.EMAIL,
                scheduled_at=datetime.utcnow(),
                sent=False
            )
            session.add(notif)
            session.commit()
            created_notifications += 1

            # enviar mail en background
            subject = "Lana App — Pago recurrente sin presupuesto suficiente"
            html = f"<p>{message}</p>"
            background_tasks.add_task(_send_mailgun_email, user.email, subject, html)

    return {"checked_until": str(cutoff), "notifications_created": created_notifications}
