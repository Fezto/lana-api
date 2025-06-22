# scripts/seed.py

import random
from datetime import date, timedelta
from faker import Faker
from sqlmodel import Session
from app.database import engine

from app.models import (
    User, Category, Budget,
    Transaction, RecurringPayment,
    Notification, RefreshToken,
    PasswordReset, EmailVerification
)
from app.utils.hash import get_password_hash

fake = Faker()


def seed_users(session: Session, n=10):
    users = []
    for _ in range(n):
        u = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            telephone=fake.phone_number(),
            password_hash=get_password_hash("secret123"),
            email_verified=random.choice([True, False])
        )
        session.add(u)
        users.append(u)
    session.commit()
    for u in users:
        session.refresh(u)
    return users


def seed_categories(session: Session, users):
    categories = []
    for u in users:
        for name, typ in [("Comida","expense"), ("Transporte","expense"),
                          ("Entretenimiento","expense"), ("Salario","income")]:
            c = Category(user_id=u.id, name=name, type=typ)
            session.add(c)
            categories.append(c)
    session.commit()
    for c in categories:
        session.refresh(c)
    return categories


def seed_budgets(session: Session, users, categories):
    budgets = []
    month = date.today().strftime("%Y-%m")
    for u in users:
        user_cats = [c for c in categories if c.user_id == u.id and c.type == "expense"]
        for c in user_cats:
            b = Budget(
                user_id=u.id,
                category_id=c.id,
                amount=round(random.uniform(100, 1000), 2),
                month_year=month
            )
            session.add(b)
            budgets.append(b)
    session.commit()
    for b in budgets:
        session.refresh(b)
    return budgets


def seed_transactions(session: Session, users, categories, budgets, n=100):
    txs = []
    for _ in range(n):
        u = random.choice(users)
        c = random.choice([c for c in categories if c.user_id == u.id])
        day = random.randint(1, 28)
        d = date.today().replace(day=day)
        amount = round(
            random.uniform(
                10,
                next((b.amount for b in budgets if b.user_id == u.id and b.category_id == c.id), 100)
            ), 2
        )
        status = random.choices(["completed", "pending", "failed"], [0.7, 0.2, 0.1])[0]
        tx = Transaction(
            user_id=u.id,
            category_id=c.id,
            amount=amount,
            date=d,
            description=fake.sentence(nb_words=6),
            type=random.choice(["manual", "auto"]),
            status=status
        )
        session.add(tx)
        txs.append(tx)
    session.commit()
    for tx in txs:
        session.refresh(tx)
    return txs


def seed_recurring(session: Session, users, categories, n=20):
    recs = []
    for _ in range(n):
        u = random.choice(users)
        c = random.choice([c for c in categories if c.user_id == u.id and c.type == "expense"] )
        freq = random.choice(["daily", "weekly", "biweekly", "monthly"])
        rp = RecurringPayment(
            user_id=u.id,
            category_id=c.id,
            amount=round(random.uniform(50, 500), 2),
            description=f"Pago {c.name}",
            frequency=freq,
            next_due_date=date.today() - timedelta(days=random.randint(0, 5)),
            active=True
        )
        session.add(rp)
        recs.append(rp)
    session.commit()
    for rp in recs:
        session.refresh(rp)
    return recs


def seed_notifications(session: Session, users, n=30):
    nots = []
    for _ in range(n):
        u = random.choice(users)
        when = date.today() + timedelta(days=random.randint(0, 10))
        notif = Notification(
            user_id=u.id,
            message=fake.sentence(nb_words=8),
            method=random.choice(["email", "sms"]),
            scheduled_at=when,
            sent=random.choice([True, False])
        )
        session.add(notif)
        nots.append(notif)
    session.commit()
    for notif in nots:
        session.refresh(notif)
    return nots


def main():
    with Session(engine) as session:
        users = seed_users(session, n=5)
        categories = seed_categories(session, users)
        budgets = seed_budgets(session, users, categories)
        seed_transactions(session, users, categories, budgets, n=50)
        seed_recurring(session, users, categories, n=10)
        seed_notifications(session, users, n=20)
    print("✅ Seeder completo.")


if __name__ == "__main__":
    main()
