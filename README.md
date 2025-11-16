# FlyBlue-Backend
FlyBlue Backend es una API moderna desarrollada con FastAPI, SQLAlchemy, JWT y PostgreSQL, diseñada para gestionar usuarios, vuelos y reservas.
Incluye autenticación segura, arquitectura limpia por capas y un conjunto completo de tests automatizados.

## Descripción
FlyBlue Backend es la API del sistema FlyBlue, encargada de:

✔ Autenticación mediante JWT
✔ Gestión de usuarios
✔ Administración de vuelos
✔ Manejo de reservas relacionadas entre usuarios y vuelos
✔ Validaciones de disponibilidad, seguridad y lógica de negocio

Está diseñada siguiendo principios de:

- Arquitectura por capas (routes → services → repositories → models)
- Inyección de dependencias
- DTOs (Data Transfer Objects)
- Buenas prácticas de FastAPI


## Tecnologias Utilizadas
| Componente        | Tecnología              |
| ----------------- | ----------------------- |
| Framework Backend | FastAPI                 |
| ORM               | SQLAlchemy              |
| Autenticación     | JWT (PyJWT)             |
| Base de datos     | PostgreSQL              |
| Contenedores      | Docker / Docker Compose |
| Testing           | PyTest + TestClient     |
| Entorno           | Python 3.10+            |

## Arquitectura (back) del Proyecto
app/
│── core/          → Seguridad, autenticación, utilidades JWT
│── db/            → Conexión y configuración de la base de datos
│── dto/           → Esquemas de entrada/salida (Pydantic)
│── models/        → Modelos SQLAlchemy (tablas)
│── repositories/  → Operaciones directas contra la BD
│── services/      → Lógica de negocio
│── routes/        → Endpoints expuestos al cliente
└── main.py        → Punto de entrada de la aplicación


## Instalación y Ejecución
### 1️Clonar el repositorio
git clone https://github.com/tu-repo/flyblue-backend.git
cd flyblue-backend

### 2️⃣ Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate

### 3️⃣ Instalar dependencias
pip install -r requirements.txt

### 4️⃣ Ejecutar el servidor
uvicorn app.main:app --reload


## Requisitos
- Python 3.10+ (recomendado)
- pip
- Docker
- PostgreSQL 
- Pytest

## Uso con Docker
Construir imagen y levantar contenedores:
```
docker-compose up --build
```

## Endpoints principales

| Módulo        | Método | Endpoint      | Descripción                    |
| ------------- | ------ | ------------- | ------------------------------ |
| Autenticación | POST   | `/auth/login` | Iniciar sesión y obtener JWT   |
| Usuarios      | CRUD   | `/usuarios/*` | Gestión completa de usuarios   |
| Vuelos        | CRUD   | `/vuelos/*`   | Administración de vuelos       |
| Reservas      | CRUD   | `/reservas/*` | Creación y control de reservas |

- Rutas protegidas: utilizan Bearer token en Authorization header

## Notas
- Los detalles de la configuración de la base de datos están en `app/db/database.py`.
- Si usas Docker, asegúrate de establecer las variables de entorno en `docker-compose.yml` o en un archivo `.env`.


## Pruebas (Tests)
- El proyecto incluye un conjunto completo de pruebas automáticas con PyTest ubicadas en la carpeta tests/.
- Estas pruebas validan cada módulo esencial del backend, asegurando que los endpoints, servicios, repositorios y autenticación funcionen correctamente.


## Cómo ejecutar los tests

### Crear y activar el entorno virtual:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

### Ejecutar las pruebas:
```
- pytest tests/test_reserva_service.py -v
- pytest tests/test_security.py -v
- pytest tests/test_usuario_service.py -v
- pytest tests/test_vuelo_service.py -v
```

| Archivo                   | Área probada                                          | Estado         |
| ------------------------- | ----------------------------------------------------- | -------------- |
| `conftest.py`             | Configuración global, cliente de pruebas, BD temporal | ✔️             |
| `test_security.py`        | Login, JWT, acceso protegido                          | ✔ Passed 12/12 |
| `test_usuario_service.py` | CRUD usuarios, validaciones, errores                  | ✔ Passed 14/14 |
| `test_vuelo_service.py`   | CRUD vuelos, disponibilidad                           | ✔ Passed 14/14 |
| `test_reserva_service.py` | CRUD reservas, validación lógica                      | ✔ Passed 15/15 |

## Estructura del proyecto
FLYBLUE-BACKEND 
│ ├── .pytest_cache/ 
│ ├── app/ 
│ ├── __pycache__/ 
│ │ │ ├── core/ 
│ │ ├── __pycache__/ 
│ │ ├── auth.py 
│ │ └── security.py 
│ │ │ ├── db/ 
│ │ ├── __pycache__/ 
│ │ └── database.py 
│ │ │ ├── dto/ 
│ │ ├── __pycache__/ 
│ │ ├── auth_dto.py 
│ │ ├── reserva_dto.py 
│ │ ├── usuario_dto.py 
│ │ └── vuelo_dto.py 
│ │ │ ├── models/ 
│ │ ├── __pycache__/ 
│ │ ├── reserva.py 
│ │ ├── usuario.py 
│ │ └── vuelo.py 
│ │ │ ├── repositories/ 
│ │ ├── __pycache__/ 
│ │ ├── reserva_repo.py 
│ │ ├── usuario_repo.py 
│ │ └── vuelo_repo.py 
│ │ │ ├── routes/ 
│ │ ├── __pycache__/ 
│ │ ├── auth_routes.py 
│ │ ├── reserva_routes.py 
│ │ ├── usuario_routes.py 
│ │ └── vuelo_routes.py 
│ │ │ ├── services/ 
│ │ ├── __pycache__/ 
│ │ ├── auth_service.py 
│ │ ├── reserva_service.py 
│ │ ├── usuario_service.py 
│ │ ├── vuelo_service.py 
│ │ └── main.py 
│ ├── tests/ 
│ ├── __pycache__/ 
│ ├── __init__.py 
│ ├── conftest.py 
│ ├── test_reserva_service.py 
│ ├── test_security.py 
│ ├── test_usuario_service.py 
│ ├── test_vuelo_service.py 
├──venv 
├──.env 
├──.gitignore 
├──docker_compose.yml 
├──Dockerfile 
├──README.md 
└── requirements.txt