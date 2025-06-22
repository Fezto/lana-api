from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import Optional


from app.models import Budget
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.session import get_session


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post(
    "/",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createBudget"
)
def create_budget(
    *,
    session: Session = Depends(get_session),
    budget_in: BudgetCreate
):
    # Prevenir duplicados (porque tienes UNIQUE en user_id, category_id, month_year)
    existing = session.exec(
        select(Budget).where(
            Budget.user_id == budget_in.user_id,
            Budget.category_id == budget_in.category_id,
            Budget.month_year == budget_in.month_year
        )
    ).one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Budget already exists for this month and category")

    budget = Budget.from_orm(budget_in)
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.get(
    "/",
    response_model=list[BudgetRead],
    operation_id="listBudgets"
)
def list_budgets(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    month_year: Optional[str] = Query(None, description="Format YYYY-MM")
):
    query = select(Budget).where(Budget.user_id == user_id)
    if month_year:
        query = query.where(Budget.month_year == month_year)
    return session.exec(query).all()


@router.get(
    "/{budget_id}",
    response_model=BudgetRead,
    operation_id="getBudget"
)
def get_budget(
    *,
    session: Session = Depends(get_session),
    budget_id: int
):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put(
    "/{budget_id}",
    response_model=BudgetRead,
    operation_id="updateBudget"
)
def update_budget(
    *,
    session: Session = Depends(get_session),
    budget_id: int,
    budget_in: BudgetUpdate
):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    for key, value in budget_in.model_dump(exclude_unset=True).items():
        setattr(budget, key, value)

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteBudget"
)
def delete_budget(
    *,
    session: Session = Depends(get_session),
    budget_id: int
):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    session.delete(budget)
    session.commit()
