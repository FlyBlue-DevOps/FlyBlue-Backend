from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# Leer la URL de la base de datos del entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no hay DATABASE_URL (sin Postgres), usar SQLite temporal
if not DATABASE_URL:
    print("⚠️ No se encontró DATABASE_URL, usando SQLite temporal en memoria.")
    DATABASE_URL = "sqlite:///:memory:"
print(f"🔗 Base de datos conectada a: {DATABASE_URL}")

# Crear el motor de conexión
engine = create_engine(DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear una sesión local para interactuar con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener una sesión en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
