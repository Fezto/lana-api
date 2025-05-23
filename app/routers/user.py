# app/api/routers/users.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.session import get_session
from app.utils.hash import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead], summary="List users")
def api_read_users(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserRead, summary="Get a user by ID")
def api_read_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def api_create_user(*, session: Session = Depends(get_session), user_in: UserCreate):
    user = User(**user_in.model_dump(exclude_unset=True), password_hash=get_password_hash(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead, summary="Update a user")
def api_update_user(*, session: Session = Depends(get_session), user_id: int, user_in: UserUpdate):
    user = session.get(User, user_id)

    user_data = user_in.model_dump(exclude_unset=True)

    if "password" in user_data:
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))

    user.sqlmodel_update(user_data)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def api_delete_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()
