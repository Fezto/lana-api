# database.py

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from app.config import DATABASE_URL
from app import models

# Inicialización del motor de la base de datos
engine = create_engine(DATABASE_URL)

# Función para manejar el ciclo de vida de la aplicación
def lifespan(app: FastAPI):
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    yield
