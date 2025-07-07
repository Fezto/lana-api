# seed_data.py
from datetime import date, datetime, timedelta
from sqlmodel import SQLModel, Session
from app.models import User, Category, Budget, Transaction, RecurringPayment, Notification
from app.utils.hash import get_password_hash
from app.session import engine  # ✅ Importar el engine existente


def create_schema():
    SQLModel.metadata.create_all(engine)


def seed_user(session: Session) -> User:
    hashed = get_password_hash("string")
    user = User(
        first_name="Test",
        last_name="User",
        email="122043099@upq.edu.mx",
        telephone="555-1234",
        password_hash=hashed,
        email_verified=True,
        created_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_categories(session: Session, user: User):
    cats = []
    for name, ctype in [("Salario", "income"), ("Ventas", "income"),
                        ("Comida", "expense"), ("Transporte", "expense")]:
        cat = Category(user_id=user.id, name=name, type=ctype)
        session.add(cat)
        cats.append(cat)
    session.commit()
    return cats


def seed_budgets(session: Session, user: User, categories):
    today = date.today()
    budgets = []
    # crea presupuestos para los últimos 3 meses
    for i in range(3):
        m = (today.month - i - 1) % 12 + 1
        y = today.year if today.month - i > 0 else today.year - 1
        month_year = f"{y}-{m:02d}"
        for cat in categories:
            # sólo gastos
            if cat.type == "expense":
                b = Budget(
                    user_id=user.id,
                    category_id=cat.id,
                    amount=200.00 + i * 50,  # varía un poco
                    month_year=month_year,
                )
                session.add(b)
                budgets.append(b)
    session.commit()
    return budgets


def seed_transactions(session: Session, user: User, categories):
    txs = []
    # últimos 15 días
    for i in range(1, 16):
        d = date.today() - timedelta(days=i)
        # una transacción de ingreso y otra de gasto al día
        income_cat = next(c for c in categories if c.type == "income")
        expense_cat = next(c for c in categories if c.type == "expense")
        txs.append(Transaction(
            user_id=user.id, category_id=income_cat.id,
            amount=1000.00 + i * 10, date=d,
            description=f"Ingreso del día {i}", type="manual", status="completed"
        ))
        txs.append(Transaction(
            user_id=user.id, category_id=expense_cat.id,
            amount=20.00 + i, date=d,
            description=f"Gasto del día {i}", type="manual", status="completed"
        ))
    session.add_all(txs)
    session.commit()
    return txs


def seed_recurring_payments(session: Session, user: User, categories):
    recs = []
    expense_cat = next(c for c in categories if c.type == "expense")
    # pago mensual de renta
    recs.append(RecurringPayment(
        user_id=user.id,
        category_id=expense_cat.id,
        amount=500.00,
        description="Renta mensual",
        frequency="monthly",
        next_due_date=date.today().replace(day=1),
        active=True,
    ))
    # pago semanal de suscripción
    recs.append(RecurringPayment(
        user_id=user.id,
        category_id=expense_cat.id,
        amount=15.00,
        description="Subscripción semanal",
        frequency="weekly",
        next_due_date=date.today() - timedelta(days=date.today().weekday()),
        active=True,
    ))
    session.add_all(recs)
    session.commit()
    return recs


def seed_notifications(session: Session, user: User):
    notes = []
    now = datetime.utcnow()
    for i in range(5):
        notes.append(Notification(
            user_id=user.id,
            message=f"Notificación de prueba #{i+1}",
            method="email" if i % 2 == 0 else "sms",
            scheduled_at=now + timedelta(hours=i),
        ))
    session.add_all(notes)
    session.commit()
    return notes


def main():
    create_schema()
    with Session(engine) as session:  # ✅ Usar el engine importado
        user = seed_user(session)
        categories = seed_categories(session, user)
        seed_budgets(session, user, categories)
        seed_transactions(session, user, categories)
        seed_recurring_payments(session, user, categories)
        seed_notifications(session, user)
    print("✅ Datos de prueba insertados exitosamente.")


if __name__ == "__main__":
    main()