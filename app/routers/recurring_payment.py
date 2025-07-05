from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional

from app.models import RecurringPayment, User
from app.schemas.recurring_payment import (
    RecurringPaymentCreate,
    RecurringPaymentRead,
    RecurringPaymentUpdate
)
from app.session import get_session
from app.utils.user import get_current_user  # Cambiar import

router = APIRouter(prefix="/recurring-payments", tags=["recurring-payments"])

@router.post(
    "/",
    response_model=RecurringPaymentRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createRecurringPayment"
)
def create_recurring_payment(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # OAuth
    rp_in: RecurringPaymentCreate
):
    rp = RecurringPayment.from_orm(rp_in)
    rp.user_id = current_user.id  # Asignar automáticamente
    session.add(rp)
    session.commit()
    session.refresh(rp)
    return rp

@router.get(
    "/",
    response_model=list[RecurringPaymentRead],
    operation_id="listRecurringPayments"
)
def list_recurring_payments(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # OAuth en lugar de user_id
    active: Optional[bool] = Query(None)
):
    query = select(RecurringPayment).where(RecurringPayment.user_id == current_user.id)
    if active is not None:
        query = query.where(RecurringPayment.active == active)
    return session.exec(query).all()

@router.get(
    "/{recurring_payment_id}",
    response_model=RecurringPaymentRead,
    operation_id="getRecurringPayment"
)
def get_recurring_payment(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    recurring_payment_id: int
):
    rp = session.get(RecurringPayment, recurring_payment_id)
    if not rp or rp.user_id != current_user.id:  # Verificar propiedad
        raise HTTPException(status_code=404, detail="Recurring payment not found")
    return rp

@router.put(
    "/{recurring_payment_id}",
    response_model=RecurringPaymentRead,
    operation_id="updateRecurringPayment"
)
def update_recurring_payment(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    recurring_payment_id: int,
    rp_in: RecurringPaymentUpdate
):
    rp = session.get(RecurringPayment, recurring_payment_id)
    if not rp or rp.user_id != current_user.id:  # Verificar propiedad
        raise HTTPException(status_code=404, detail="Recurring payment not found")

    for key, value in rp_in.model_dump(exclude_unset=True).items():
        setattr(rp, key, value)

    session.add(rp)
    session.commit()
    session.refresh(rp)
    return rp

@router.delete(
    "/{recurring_payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteRecurringPayment"
)
def delete_recurring_payment(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    recurring_payment_id: int
):
    rp = session.get(RecurringPayment, recurring_payment_id)
    if not rp or rp.user_id != current_user.id:  # Verificar propiedad
        raise HTTPException(status_code=404, detail="Recurring payment not found")

    session.delete(rp)
    session.commit()