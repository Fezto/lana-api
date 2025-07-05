from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.models import Category, User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.session import get_session
from app.utils.user import get_current_user  # Cambiar import

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
    current_user: User = Depends(get_current_user),  # OAuth
    category_in: CategoryCreate
):
    category = Category.from_orm(category_in)
    category.user_id = current_user.id  # Asignar automáticamente
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
    current_user: User = Depends(get_current_user)  # OAuth en lugar de user_id
):
    categories = session.exec(
        select(Category).where(Category.user_id == current_user.id)
    ).all()
    return categories

@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    operation_id="getCategory"
)
def get_category(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    category_id: int
):
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:  # Verificar propiedad
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
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    category_id: int,
    category_in: CategoryUpdate
):
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:  # Verificar propiedad
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
    current_user: User = Depends(get_current_user),  # Agregar OAuth
    category_id: int
):
    category = session.get(Category, category_id)
    if not category or category.user_id != current_user.id:  # Verificar propiedad
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()