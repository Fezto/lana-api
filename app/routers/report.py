from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from sqlalchemy import case
from datetime import date
from typing import Optional, Literal


from app.session import get_session
from app.models import Transaction, Category, User
from app.schemas.report import (
    IncomeExpenseItem, IncomeExpenseResponse,
    CategoryReportItem, CategoryReportResponse,
    TrendItem, TrendReportResponse
)
from app.utils.user import get_current_user  # Agregar import

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get(
    "/income-expense",
    response_model=IncomeExpenseResponse,
    operation_id="getIncomeExpenseReport"
)
def get_income_expense(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    start_date: date = Query(...),
    end_date: date = Query(...)
):
    """Totales de ingresos vs gastos por mes dentro de un rango de fechas."""
    stmt = (
        select(
            func.date_format(Transaction.date, '%Y-%m').label('period'),
            func.sum(
                case(
                    (Category.type == 'income', Transaction.amount),
                    else_=0
                )
            ).label('income'),
            func.sum(
                case(
                    (Category.type == 'expense', Transaction.amount),
                    else_=0
                )
            ).label('expense')
        )
        .join(Category, Category.id == Transaction.category_id)
        .where(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        .group_by('period')
        .order_by('period')
    )
    results = session.exec(stmt).all()
    items = [IncomeExpenseItem(**r._asdict()) for r in results]
    return IncomeExpenseResponse(items=items)
@router.get(
    "/by-category",
    response_model=CategoryReportResponse,
    operation_id="getByCategoryReport"
)
def get_by_category(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # OAuth en lugar de user_id
    start_date: date = Query(...),
    end_date: date = Query(...),
    type: Optional[Literal['income','expense']] = Query(None)
):
    """Totales por categoría dentro de un rango de fechas."""
    stmt = (
        select(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.sum(Transaction.amount).label('total')
        )
        .join(Category, Category.id == Transaction.category_id)
        .where(
            Transaction.user_id == current_user.id,  # Usar current_user.id
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
    )
    if type:
        stmt = stmt.where(Category.type == type)
    stmt = stmt.group_by(Category.id, Category.name).order_by(Category.name)
    results = session.exec(stmt).all()
    items = [CategoryReportItem(**r._asdict()) for r in results]
    return CategoryReportResponse(
        start_date=start_date,
        end_date=end_date,
        items=items
    )

@router.get(
    "/trends",
    response_model=TrendReportResponse,
    operation_id="getTrendReport"
)
def get_trends(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # OAuth en lugar de user_id
    start_date: date = Query(...),
    end_date: date = Query(...),
    granularity: Literal['daily','weekly','monthly'] = Query('daily')
):
    """Serie temporal de transacciones por periodo."""
    if granularity == 'daily':
        period_expr = func.date_format(Transaction.date, '%Y-%m-%d')
    elif granularity == 'monthly':
        period_expr = func.date_format(Transaction.date, '%Y-%m')
    else:  # weekly
        period_expr = func.concat(
            func.date_format(Transaction.date, '%Y'),
            '-W', func.week(Transaction.date)
        )

    stmt = (
        select(
            period_expr.label('period'),
            func.sum(Transaction.amount).label('total')
        )
        .where(
            Transaction.user_id == current_user.id,  # Usar current_user.id
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        .group_by('period')
        .order_by('period')
    )
    results = session.exec(stmt).all()
    items = [TrendItem(**r._asdict()) for r in results]
    return TrendReportResponse(
        granularity=granularity,
        items=items
    )