# tests/conftest.py
"""
Configuración central de PyTest con fixtures compartidos.

Fixtures son funciones que preparan datos de prueba reutilizables.
PyTest las inyecta automáticamente en las funciones de test.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.core.security import get_password_hash
from app.models.notificacion import Notificacion


# CRÍTICO: Importar TODOS los modelos ANTES de crear las tablas
# Esto asegura que Base.metadata tenga conocimiento de todas las tablas
from app.models.usuario import Usuario
from app.models.vuelo import Vuelo
from app.models.reserva import Reserva

# Importar app DESPUÉS de los modelos
from app.main import app

# ========== BASE DE DATOS DE PRUEBA ==========

@pytest.fixture(scope="function")
def db_engine():
    """
    Crea un motor de base de datos temporal para cada test.
    
    scope="function" → Se ejecuta antes de CADA test y se limpia después.
    Esto garantiza que cada test tenga una BD limpia.
    
    IMPORTANTE: Usa SQLite en memoria (:memory:) para máxima velocidad.
    """
    # Crear engine con SQLite en memoria
    engine = create_engine(
        "sqlite:///:memory:",  # Base de datos en RAM (súper rápido)
        connect_args={"check_same_thread": False},
        poolclass=None  # Desactivar pool de conexiones para tests
    )
    
    # Habilitar foreign keys en SQLite (importante para relaciones)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Limpiar después del test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Proporciona una sesión de base de datos para cada test.
    
    Uso en tests:
        def test_algo(db_session):
            usuario = Usuario(...)
            db_session.add(usuario)
            db_session.commit()
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
        expire_on_commit=False  # Evitar que los objetos expiren después de commit
    )
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def client(db_session, db_engine):
    """
    Cliente HTTP de prueba que usa la BD de test.
    
    CRÍTICO: Inyecta tanto db_session como db_engine para asegurar
    que las tablas existan antes de que FastAPI las use.
    
    Uso en tests:
        def test_login(client):
            response = client.post("/auth/login", json={...})
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # db_session.close() se maneja en el fixture db_session
    
    # CRÍTICO: Sobrescribir la dependencia get_db de FastAPI
    app.dependency_overrides[get_db] = override_get_db
    
    # Crear el cliente de prueba
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar después del test
    app.dependency_overrides.clear()


# ========== DATOS DE PRUEBA ==========
@pytest.fixture
def usuario_cliente_data():
    """
    Datos para crear un usuario con rol 'cliente'.
    """
    return {
        "id": 12345678,
        "nombre": "Juan Pérez",
        "email": "juan@test.com",
        "contrasena": "password123",
        "rol": "cliente"
    }


@pytest.fixture
def usuario_admin_data():
    """
    Datos para crear un usuario con rol 'admin'.
    """
    return {
        "id": 87654321,
        "nombre": "Admin Test",
        "email": "admin@test.com",
        "contrasena": "admin123",
        "rol": "admin"
    }


@pytest.fixture
def vuelo_data():
    """
    Datos para crear un vuelo de prueba.
    """
    from datetime import datetime, timedelta
    
    return {
        "id": 100,
        "origen": "Ibagué (IBG)",
        "destino": "Medellín (MDE)",
        "salida": datetime.utcnow() + timedelta(days=7),
        "llegada": datetime.utcnow() + timedelta(days=7, hours=2),
        "duracion": 2.0,
        "precio_base": 150000.0,
        "asientos_disponibles": 50
    }


@pytest.fixture
def reserva_data():
    """
    Datos para crear una reserva de prueba.
    """
    return {
        "vuelo_id": 100,
        "clase": "económica",
        "asiento": "12A",
        "total": 150000.0
    }


# ========== HELPERS ==========
@pytest.fixture
def create_usuario(db_session):
    """
    Helper para crear usuarios en la BD de test.
    
    Uso:
        def test_algo(create_usuario, usuario_cliente_data):
            usuario = create_usuario(usuario_cliente_data)
            assert usuario.id == 12345678
    """
    def _create_usuario(data: dict):
        usuario = Usuario(
            id=data["id"],
            nombre=data["nombre"],
            email=data["email"],
            contrasena=get_password_hash(data["contrasena"]),
            rol=data.get("rol", "cliente")
        )
        db_session.add(usuario)
        db_session.commit()
        db_session.refresh(usuario)
        return usuario
    
    return _create_usuario


@pytest.fixture
def create_vuelo(db_session):
    """
    Helper para crear vuelos en la BD de test.
    """
    from app.models.vuelo import Vuelo
    
    def _create_vuelo(data: dict):
        vuelo = Vuelo(**data)
        db_session.add(vuelo)
        db_session.commit()
        db_session.refresh(vuelo)
        return vuelo
    
    return _create_vuelo


@pytest.fixture
def get_auth_headers(client, create_usuario, usuario_cliente_data):
    """
    Helper para obtener headers de autenticación JWT.
    
    Uso:
        def test_endpoint_protegido(client, get_auth_headers):
            headers = get_auth_headers()
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 200
    """
    def _get_headers(user_data=None):
        if user_data is None:
            user_data = usuario_cliente_data
        
        # Crear usuario
        create_usuario(user_data)
        
        # Login para obtener token
        response = client.post("/auth/login", json={
            "email": user_data["email"],
            "contrasena": user_data["contrasena"]
        })
        
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return _get_headers

@pytest.fixture
def create_servicio(db_session):
    """
    Helper para crear servicios adicionales en la BD de test.

    Uso:
        servicio = create_servicio({
            "nombre": "Wifi",
            "descripcion": "Internet",
            "precio": 20000
        })
    """
    from app.models.servicio import Servicio

    def _create_servicio(data: dict):
        servicio = Servicio(**data)
        db_session.add(servicio)
        db_session.commit()
        db_session.refresh(servicio)
        return servicio

    return _create_servicio

@pytest.fixture
def create_reserva(db_session):
    """
    Helper para crear reservas en la BD de test.

    Uso:
        reserva = create_reserva({
            "usuario_id": ...,
            "vuelo_id": ...,
            "clase": "económica",
            "asiento": "12A",
            "total": 150000.0
        })
    """
    from app.models.reserva import Reserva

    def _create_reserva(data: dict):
        reserva = Reserva(**data)
        db_session.add(reserva)
        db_session.commit()
        db_session.refresh(reserva)
        return reserva

    return _create_reserva

@pytest.fixture
def create_pago(db_session):
    """
    Helper para crear pagos en la BD de test.

    Uso:
        pago = create_pago({
            "reserva_id": 1,
            "monto": 100000,
            "metodo": "tarjeta",
            "estado": "pendiente"
        })
    """
    from app.models.pago import Pago

    def _create_pago(data: dict):
        pago = Pago(**data)
        db_session.add(pago)
        db_session.commit()
        db_session.refresh(pago)
        return pago

    return _create_pago

@pytest.fixture
def create_notificacion(db_session):
    """
    Fixture para crear notificaciones correctamente relacionadas con un usuario válido.
    Si el usuario no existe, se crea automáticamente.
    """

    def _create_notificacion(data: dict):
        usuario_id = data.get("usuario_id")

        # Verificar si el usuario existe, si no, crearlo
        usuario = db_session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            nuevo_usuario = Usuario(
                id=usuario_id,
                nombre="Usuario Test",
                email=f"user{usuario_id}@test.com",
                contrasena="test"
            )
            db_session.add(nuevo_usuario)
            db_session.commit()
            db_session.refresh(nuevo_usuario)

        nueva_notificacion = Notificacion(
            usuario_id=usuario_id,
            titulo=data.get("titulo"),
            mensaje=data.get("mensaje"),
            tipo=data.get("tipo", "info"),
            leido=False
        )

        db_session.add(nueva_notificacion)
        db_session.commit()
        db_session.refresh(nueva_notificacion)

        return nueva_notificacion

    return _create_notificacion
