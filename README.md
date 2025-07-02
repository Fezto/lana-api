# Lana

Lana es una aplicación de gestión financiera personal desarrollada en Python. Permite a los usuarios gestionar
presupuestos, categorías, transacciones, pagos recurrentes, notificaciones y más.

## Características principales

- Registro y autenticación de usuarios
- Gestión de presupuestos y categorías
- Registro de transacciones
- Pagos recurrentes
- Notificaciones por correo electrónico
- Reportes y resúmenes de gastos

## Estructura del proyecto

```
app/
  main.py                # Punto de entrada de la aplicación
  config.py              # Configuración del env
  database.py            # Configuración de la base de datos
  seeder.py              # Datos de ejemplo
  session.py             # Manejo de sesiones
  models/                # Modelos de la base de datos
  routers/               # Rutas de la API (FastAPI)
  schemas/               # Esquemas Pydantic
  utils/                 # Utilidades (hash, email, tokens, etc)
```

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Fezto/lana-api
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Genera tu .env dentro de la raiz del proyecto:
   ```dotenv
   # Base de datos
   # ESTO ES LO ÚNICO QUE DEBES DE CAMBIAR!
   DATABASE_USER=root
   DATABASE_HOST=localhost
   DATABASE_PASSWORD='<Cambia esto por tu contraseña de MySQL'
   DATABASE_NAME=lana
   
   # Secret de JWT
   JWT_SECRET='<Coloca un string cualquiera aquí>'
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTE=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Mailgun Sandbox - Nuestro servicio de correos
   # Todo esto se comparte de manera personal
   MAILGUN_API_KEY='<Cámbialo con lo que se te comparta'
   MAILGUN_DOMAIN='<Cámbialo con lo que se te comparta>'
   MAIL_FROM_ADDRESS='<Cámbialo con lo que se te comparta>'
   MAIL_FROM_NAME=Lana

   # URL de tu API (Por el momento localhost)
   API_URL=http://localhost:8000
   ```
4. Crea una base de datos llamada 'lana':
   ```sql
   CREATE DATABASE lana;
   ```
## Uso
1. Ejecuta la aplicación:
   ```bash
   fastapi run
   ```

2. Accede a la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs) (si usas FastAPI).

## Requisitos

- Python 3.10+
- Las dependencias listadas en `requirements.txt`

## Licencia

MIT