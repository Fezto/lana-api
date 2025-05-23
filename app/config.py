from os import getenv
from dotenv import load_dotenv

load_dotenv()

DATABASE_USER=getenv("DATABASE_USER")
DATABASE_HOST=getenv("DATABASE_HOST")
DATABASE_PASSWORD=getenv("DATABASE_PASSWORD")
DATABASE_NAME=getenv("DATABASE_NAME")

# Configuración de la base de datos
DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:3306/{DATABASE_NAME}"