from datetime import timedelta, date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.models import Transaction, RecurringPayment
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate
)
from app.session import get_session

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createTransaction"
)
def create_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_in: TransactionCreate
):
    transaction = Transaction.from_orm(transaction_in)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get(
    "/",
    response_model=list[TransactionRead],
    operation_id="listTransactions"
)
def list_transactions(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    start_date: str = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str = Query(None, description="End date YYYY-MM-DD")
):
    query = select(Transaction).where(Transaction.user_id == user_id)

    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)

    transactions = session.exec(query).all()
    return transactions


@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
    operation_id="getTransaction"
)
def get_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_id: int
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put(
    "/{transaction_id}",
    response_model=TransactionRead,
    operation_id="updateTransaction"
)
def update_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_id: int,
    transaction_in: TransactionUpdate
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in transaction_in.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteTransaction"
)
def delete_transaction(
    *,
    session: Session = Depends(get_session),
    transaction_id: int
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()
    return

@router.post(
    "/generate-recurring",
    response_model=list[TransactionRead],
    status_code=status.HTTP_201_CREATED,
    operation_id="generateRecurringTransactions"
)
def generate_recurring_transactions(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    today: date = Depends(lambda: date.today())
):
    """
    Busca todos los recurring_payments con next_due_date <= today y active=True,
    crea una transaction por cada uno y actualiza next_due_date al siguiente ciclo.
    """
    # 1. Traer pagos fijos pendientes
    recs = session.exec(
        select(RecurringPayment)
        .where(
            RecurringPayment.user_id == user_id,
            RecurringPayment.active == True,
            RecurringPayment.next_due_date <= today
        )
    ).all()

    if not recs:
        raise HTTPException(status_code=404, detail="No recurring payments to generate")

    created: list[Transaction] = []
    for rp in recs:
        # 2. Crear transacción
        tx = Transaction(
            user_id=rp.user_id,
            category_id=rp.category_id,
            amount=rp.amount,
            date=rp.next_due_date,
            description=rp.description,
            type="auto",
            status="pending",
            recurring_id=rp.id
        )
        session.add(tx)
        created.append(tx)

        # 3. Calcular next_due_date según frecuencia
        if rp.frequency == "daily":
            rp.next_due_date += timedelta(days=1)
        elif rp.frequency == "weekly":
            rp.next_due_date += timedelta(weeks=1)
        elif rp.frequency == "biweekly":
            rp.next_due_date += timedelta(weeks=2)
        elif rp.frequency == "monthly":
            # simple: sumar 1 mes saltando fin de mes
            yr, m = divmod(rp.next_due_date.year * 12 + rp.next_due_date.month, 12)
            rp.next_due_date = rp.next_due_date.replace(year=yr, month=m+1)
        # si quisieras inactivar cuando fallen, podrías rp.active = False

        session.add(rp)

    # 4. Commit todo junto
    session.commit()
    for tx in created:
        session.refresh(tx)

    return [TransactionRead.from_orm(tx) for tx in created]
