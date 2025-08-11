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

@router.post("/run-checks", status_code=status.HTTP_200_OK, operation_id="runNotificationChecks")
def run_notification_checks(
    *,
    session: Session = Depends(get_session),
    background_tasks: BackgroundTasks,
    days_ahead: int = 2  # Por defecto, verificar pagos en los próximos 2 días
):
    today = date.today()
    upcoming_date = today + timedelta(days=days_ahead)

    # Buscar pagos recurrentes programados dentro de los próximos días
    recurring_payments = session.exec(
        select(RecurringPayment).where(
            RecurringPayment.next_due_date >= today,
            RecurringPayment.next_due_date <= upcoming_date,
            RecurringPayment.active == True
        )
    ).all()

    if not recurring_payments:
        return {"message": "No hay pagos recurrentes próximos."}

    for rp in recurring_payments:
        # Verificar presupuesto disponible para la categoría del pago recurrente
        month_year = f"{rp.next_due_date.year}-{rp.next_due_date.month:02d}"
        budget = session.exec(
            select(Budget).where(
                Budget.user_id == rp.user_id,
                Budget.category_id == rp.category_id,
                Budget.month_year == month_year
            )
        ).first()

        # Calcular el presupuesto restante
        if budget:
            # Calcular lo gastado en la categoría/mes
            start_date = date(rp.next_due_date.year, rp.next_due_date.month, 1)
            if rp.next_due_date.month == 12:
                next_month = date(rp.next_due_date.year + 1, 1, 1)
            else:
                next_month = date(rp.next_due_date.year, rp.next_due_date.month + 1, 1)

            transactions = session.exec(
                select(Transaction).where(
                    Transaction.user_id == rp.user_id,
                    Transaction.category_id == rp.category_id,
                    Transaction.date >= start_date,
                    Transaction.date < next_month
                )
            ).all()
            total_spent = sum(t.amount for t in transactions)
            remaining_budget = budget.amount - total_spent
        else:
            remaining_budget = 0  # No hay presupuesto asignado para esta categoría

        # Si no hay suficiente presupuesto, generar notificación y enviar correo
        if rp.amount > remaining_budget:
            user = session.get(User, rp.user_id)
            if not user:
                continue

            message = (
                f"El pago recurrente '{rp.description}' programado para el "
                f"{rp.next_due_date} no tiene suficiente presupuesto. "
                f"Presupuesto disponible: {remaining_budget:.2f}. "
                f"Monto requerido: {rp.amount:.2f}."
            )

            # Crear notificación
            notification = Notification(
                user_id=rp.user_id,
                message=message,
                method=NotificationMethod.EMAIL,
                scheduled_at=datetime.utcnow(),
                sent=False
            )
            session.add(notification)

            # Enviar correo en segundo plano
            subject = "Lana App — Alerta de presupuesto insuficiente"
            html = f"<p>{message}</p>"
            background_tasks.add_task(_send_mailgun_email, user.email, subject, html)

    session.commit()
    return {"message": "Verificación de notificaciones completada."}
