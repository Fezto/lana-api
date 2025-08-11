# app/routers/transaction.py  (reemplazar imports al inicio)
from datetime import timedelta, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session, select

from app.models import Transaction, RecurringPayment, User, Category, Budget, Notification
from app.enums.notification_method import NotificationMethod
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate
)
from app.session import get_session
from app.utils.user import get_current_user  # Agregado
from app.utils.email import _send_mailgun_email  # función async de mailgun (ya existente)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createTransaction"
)
# app/routers/transaction.py  -> reemplazar la función create_transaction
def create_transaction(
        *,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        transaction_in: TransactionCreate,
        background_tasks: BackgroundTasks
):
    # Construir transacción con user_id
    transaction = Transaction(
        **transaction_in.model_dump(),
        user_id=current_user.id
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    # --- Comprobación del presupuesto de la categoría/mes ---
    # convertir fecha a month_year tipo 'YYYY-MM'
    tx_date = transaction.date or date.today()
    month_year = f"{tx_date.year}-{tx_date.month:02d}"

    # buscar presupuesto para user/category/month
    budget = session.exec(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == transaction.category_id,
            Budget.month_year == month_year
        )
    ).first()

    if budget:
        # calcular lo gastado en ese mes y categoría
        start_date = date(tx_date.year, tx_date.month, 1)
        if tx_date.month == 12:
            next_month = date(tx_date.year + 1, 1, 1)
        else:
            next_month = date(tx_date.year, tx_date.month + 1, 1)

        txs = session.exec(
            select(Transaction).where(
                Transaction.user_id == current_user.id,
                Transaction.category_id == transaction.category_id,
                Transaction.date >= start_date,
                Transaction.date < next_month
            )
        ).all()
        total_spent = sum(t.amount for t in txs)

        # si se supera el presupuesto -> crear Notification + enviar email en background
        if total_spent > budget.amount:
            message = (
                f"Has superado el presupuesto para la categoría (id={budget.category_id}) "
                f"del mes {month_year}. Presupuesto: {budget.amount:.2f}. Gastado: {total_spent:.2f}."
            )

            notif = Notification(
                user_id=current_user.id,
                message=message,
                method=NotificationMethod.EMAIL,  # por defecto email; ver más abajo para SMS
                scheduled_at=datetime.utcnow(),
                sent=False
            )
            session.add(notif)
            session.commit()

            # Envío en background (mailgun)
            subject = "Lana App — Presupuesto superado"
            html = f"<p>{message}</p>"
            # _send_mailgun_email es async, FastAPI BackgroundTasks admite async callables
            background_tasks.add_task(_send_mailgun_email, current_user.email, subject, html)

    return transaction



@router.get(
    "/",
    response_model=list[TransactionRead],
    operation_id="listTransactions"
)
def list_transactions(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    start_date: str = Query(None, description="Start date YYYY-MM-DD"),
    end_date: str = Query(None, description="End date YYYY-MM-DD")
):
    query = (
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
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
    current_user: User = Depends(get_current_user),
    transaction_id: int
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
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
    current_user: User = Depends(get_current_user),
    transaction_id: int,
    transaction_in: TransactionUpdate
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
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
    current_user: User = Depends(get_current_user),
    transaction_id: int
):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
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
    current_user: User = Depends(get_current_user),
    today: date = Depends(lambda: date.today())
):
    recs = session.exec(
        select(RecurringPayment)
        .where(
            RecurringPayment.user_id == current_user.id,
            RecurringPayment.active == True,
            RecurringPayment.next_due_date <= today
        )
    ).all()

    if not recs:
        raise HTTPException(status_code=404, detail="No recurring payments to generate")

    created: list[Transaction] = []
    for rp in recs:
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

        if rp.frequency == "daily":
            rp.next_due_date += timedelta(days=1)
        elif rp.frequency == "weekly":
            rp.next_due_date += timedelta(weeks=1)
        elif rp.frequency == "biweekly":
            rp.next_due_date += timedelta(weeks=2)
        elif rp.frequency == "monthly":
            yr, m = divmod(rp.next_due_date.year * 12 + rp.next_due_date.month, 12)
            rp.next_due_date = rp.next_due_date.replace(year=yr, month=m+1)

        session.add(rp)

    session.commit()
    for tx in created:
        session.refresh(tx)

    return created
