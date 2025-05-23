from fastapi import FastAPI
from app.database import lifespan

# Inicialización de la aplicación FastAPI
app = FastAPI(lifespan=lifespan)


