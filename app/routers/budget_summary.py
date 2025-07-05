from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from datetime import date

from app.session import get_session
from app.models import Budget, Transaction, Category, User
from app.schemas.budget_summary import BudgetSummaryItem, BudgetSummaryResponse
from app.utils.user import get_current_user  # Agregar import

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.get(
    "/summary",
    response_model=BudgetSummaryResponse,
    operation_id="getBudgetSummary"
)
def get_budget_summary(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # OAuth en lugar de user_id
    month_year: str = Query(..., description="Mes en formato YYYY-MM")
):
    # Validar formato
    try:
        year, month = map(int, month_year.split('-'))
        start_date = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de month_year inválido")

    # Obtener presupuestos del usuario autenticado
    budgets = session.exec(
        select(Budget, Category.name)
        .join(Category, Category.id == Budget.category_id)
        .where(
            Budget.user_id == current_user.id,  # Usar current_user.id
            Budget.month_year == month_year
        )
    ).all()

    summary: list[BudgetSummaryItem] = []
    for (budget, category_name) in budgets:
        spent = session.exec(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(
                Transaction.user_id == current_user.id,  # Usar current_user.id
                Transaction.category_id == budget.category_id,
                Transaction.status == "completed",
                Transaction.date >= start_date,
                Transaction.date < next_month
            )
        ).one()

        spent_amount = float(spent or 0)
        budgeted = float(budget.amount)
        remaining = budgeted - spent_amount
        percent_used = (spent_amount / budgeted * 100) if budgeted > 0 else 0.0

        summary.append(
            BudgetSummaryItem(
                category_id=budget.category_id,
                category_name=category_name,
                budgeted_amount=budgeted,
                spent_amount=spent_amount,
                remaining=remaining,
                percent_used=percent_used
            )
        )

    return BudgetSummaryResponse(
        month_year=month_year,
        summary=summary
    )