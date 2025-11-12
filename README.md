# FlyBlue-Backend

API backend para el proyecto FlyBlue (gestión de usuarios, vuelos y reservas).

## Descripción

Este repositorio contiene una API construida con FastAPI, SQLAlchemy y JWT para autenticación. Proporciona endpoints para autenticación, gestión de usuarios, vuelos y reservas.

## Requisitos

- Python 3.10+ (recomendado)
- pip
- Docker

## Uso con Docker

Construir imagen y levantar contenedores:

```powershell
docker-compose up --build
```

## Endpoints principales

- `POST /auth/login` - Inicia sesión y devuelve token JWT
- Rutas protegidas: utilizan Bearer token en Authorization header

## Notas

- Los detalles de la configuración de la base de datos están en `app/db/database.py`.
- Si usas Docker, asegúrate de establecer las variables de entorno en `docker-compose.yml` o en un archivo `.env`.

## Licencia

Proyecto para uso académico.
