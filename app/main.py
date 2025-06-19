# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import lifespan
from app.routers.user import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Permite peticiones desde cualquier dominio
    allow_credentials=True,         # Permite credenciales (cookies, encabezados de autorización)
    allow_methods=["*"],            # Permite cualquier método (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Permite cualquier encabezado
)
app.include_router(users_router)
app.include_router(auth_router)

for route in app.routes:
    print(f"{route.path} -> {route.name}")
