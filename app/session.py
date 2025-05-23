from typing import Annotated
from sqlmodel import Session
from fastapi import Depends

from app.database import engine


def get_session():
    with Session(engine) as session: # abreme esto
        yield session                   # pausa y espera a que el programa

DatabaseSession = Annotated[Session, Depends(get_session)]