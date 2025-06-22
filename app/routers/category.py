from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.models import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.session import get_session

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="createCategory"
)
def create_category(
    *,
    session: Session = Depends(get_session),
    category_in: CategoryCreate
):
    category = Category.from_orm(category_in)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get(
    "/",
    response_model=list[CategoryRead],
    operation_id="listCategories"
)
def list_categories(
    *,
    session: Session = Depends(get_session),
    user_id: int
):
    categories = session.exec(select(Category).where(Category.user_id == user_id)).all()
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    operation_id="getCategory"
)
def get_category(
    *,
    session: Session = Depends(get_session),
    category_id: int
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    operation_id="updateCategory"
)
def update_category(
    *,
    session: Session = Depends(get_session),
    category_id: int,
    category_in: CategoryUpdate
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteCategory"
)
def delete_category(
    *,
    session: Session = Depends(get_session),
    category_id: int
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return
