# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.database import lifespan
from app.routers.user import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(auth_router)

for route in app.routes:
    print(f"{route.path} -> {route.name}")
