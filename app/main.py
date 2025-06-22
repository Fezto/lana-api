# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import lifespan
from app.routers.user import router as users_router
from app.routers.auth import router as auth_router
from app.routers.transaction import router as transaction_router
from app.routers.category import router as category_router
from app.routers.recurring_payment import router as recurring_payments_router
from app.routers.budget import router as budget_router
from app.routers.report import router as report_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de routers
routers = [
    users_router,
    auth_router,
    transaction_router,
    category_router,
    recurring_payments_router,
    budget_router,
    report_router,
]

# Incluir todos los routers
for router in routers:
    app.include_router(router)

# Mostrar rutas en consola
for route in app.routes:
    print(f"{route.path} -> {route.name}")
