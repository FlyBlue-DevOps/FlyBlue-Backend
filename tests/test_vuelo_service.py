# tests/test_vuelo_service.py
"""
Pruebas unitarias para el servicio de vuelos (services/vuelo_service.py).

Valida:
- Creación de vuelos
- Validación de códigos duplicados
- Listado de vuelos
- Filtrado de vuelos disponibles
- Actualización de datos de vuelos
- Eliminación de vuelos
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.services import vuelo_service
from app.dto.vuelo_dto import VueloCreate, VueloUpdate


# ========== PRUEBAS DE CREACIÓN ==========

def test_crear_vuelo_exitoso(db_session):
    """
    Verifica que se pueda crear un vuelo correctamente.
    """
    salida = datetime.utcnow() + timedelta(days=10)
    llegada = salida + timedelta(hours=2)
    
    datos = VueloCreate(
        id=101,
        origen="Ibagué (IBG)",
        destino="Cartagena (CTG)",
        salida=salida,
        llegada=llegada,
        duracion=2.0,
        precio_base=200000.0,
        asientos_disponibles=100
    )
    
    vuelo = vuelo_service.crear_vuelo(db_session, datos)
    
    # Verificaciones
    assert vuelo is not None
    assert vuelo.id == 101
    assert vuelo.origen == "Ibagué (IBG)"
    assert vuelo.destino == "Cartagena (CTG)"
    assert vuelo.precio_base == 200000.0
    assert vuelo.asientos_disponibles == 100


def test_crear_vuelo_id_duplicado(db_session, create_vuelo, vuelo_data):
    """
    Verifica que no se permita crear dos vuelos con el mismo ID.
    
    Debe lanzar HTTPException con código 400.
    """
    # Crear primer vuelo
    create_vuelo(vuelo_data)
    
    # Intentar crear segundo vuelo con mismo ID
    salida = datetime.utcnow() + timedelta(days=15)
    llegada = salida + timedelta(hours=3)
    
    datos_duplicados = VueloCreate(
        id=vuelo_data["id"],  # ID duplicado
        origen="Cali (CLO)",
        destino="San Andrés (ADZ)",
        salida=salida,
        llegada=llegada,
        duracion=3.0,
        precio_base=300000.0,
        asientos_disponibles=80
    )
    
    with pytest.raises(HTTPException) as exc_info:
        vuelo_service.crear_vuelo(db_session, datos_duplicados)
    
    assert exc_info.value.status_code == 400
    assert "ya existe" in exc_info.value.detail.lower()


def test_crear_vuelo_sin_asientos(db_session):
    """
    Verifica que se pueda crear un vuelo con 0 asientos disponibles.
    
    Esto es válido para vuelos que ya están completamente reservados.
    """
    salida = datetime.utcnow() + timedelta(days=5)
    llegada = salida + timedelta(hours=1.5)
    
    datos = VueloCreate(
        id=102,
        origen="Medellín (MDE)",
        destino="Santa Marta (SMR)",
        salida=salida,
        llegada=llegada,
        duracion=1.5,
        precio_base=180000.0,
        asientos_disponibles=0  # Vuelo lleno
    )
    
    vuelo = vuelo_service.crear_vuelo(db_session, datos)
    
    assert vuelo.asientos_disponibles == 0


# ========== PRUEBAS DE LISTADO ==========

def test_listar_vuelos_vacio(db_session):
    """
    Verifica que listar_vuelos() devuelva lista vacía cuando no hay vuelos.
    """
    vuelos = vuelo_service.listar_vuelos(db_session)
    
    assert vuelos == []


def test_listar_vuelos_con_datos(db_session, create_vuelo, vuelo_data):
    """
    Verifica que listar_vuelos() devuelva todos los vuelos registrados.
    """
    # Crear varios vuelos
    vuelo1 = create_vuelo(vuelo_data)
    
    salida2 = datetime.utcnow() + timedelta(days=15)
    llegada2 = salida2 + timedelta(hours=3)
    vuelo2_data = {
        "id": 200,
        "origen": "Cali (CLO)",
        "destino": "Ibagué (IBG)",
        "salida": salida2,
        "llegada": llegada2,
        "duracion": 3.0,
        "precio_base": 250000.0,
        "asientos_disponibles": 75
    }
    vuelo2 = create_vuelo(vuelo2_data)
    
    vuelos = vuelo_service.listar_vuelos(db_session)
    
    assert len(vuelos) == 2
    assert any(v.id == vuelo1.id for v in vuelos)
    assert any(v.id == vuelo2.id for v in vuelos)


# ========== PRUEBAS DE OBTENCIÓN POR ID ==========

def test_obtener_vuelo_existente(db_session, create_vuelo, vuelo_data):
    """
    Verifica que se pueda obtener un vuelo por su ID.
    """
    vuelo_creado = create_vuelo(vuelo_data)
    
    vuelo = vuelo_service.obtener_vuelo(db_session, vuelo_creado.id)
    
    assert vuelo is not None
    assert vuelo.id == vuelo_data["id"]
    assert vuelo.origen == vuelo_data["origen"]
    assert vuelo.destino == vuelo_data["destino"]


def test_obtener_vuelo_inexistente(db_session):
    """
    Verifica que obtener_vuelo() lance excepción cuando el ID no existe.
    
    Debe lanzar HTTPException con código 404.
    """
    id_inexistente = 9999
    
    with pytest.raises(HTTPException) as exc_info:
        vuelo_service.obtener_vuelo(db_session, id_inexistente)
    
    assert exc_info.value.status_code == 404
    assert "no encontrado" in exc_info.value.detail.lower()


# ========== PRUEBAS DE VUELOS DISPONIBLES ==========

def test_vuelos_disponibles_todos_con_asientos(db_session, create_vuelo):
    """
    Verifica que vuelos_disponibles() devuelva solo vuelos con asientos > 0.
    """
    salida1 = datetime.utcnow() + timedelta(days=5)
    vuelo1_data = {
        "id": 301,
        "origen": "Ibagué (IBG)",
        "destino": "Medellín (MDE)",
        "salida": salida1,
        "llegada": salida1 + timedelta(hours=2),
        "duracion": 2.0,
        "precio_base": 150000.0,
        "asientos_disponibles": 50
    }
    
    salida2 = datetime.utcnow() + timedelta(days=6)
    vuelo2_data = {
        "id": 302,
        "origen": "Cali (CLO)",
        "destino": "Cartagena (CTG)",
        "salida": salida2,
        "llegada": salida2 + timedelta(hours=2.5),
        "duracion": 2.5,
        "precio_base": 220000.0,
        "asientos_disponibles": 0  # SIN ASIENTOS
    }
    
    create_vuelo(vuelo1_data)
    create_vuelo(vuelo2_data)
    
    vuelos_disponibles = vuelo_service.vuelos_disponibles(db_session)
    
    # Solo debe devolver el vuelo con asientos disponibles
    assert len(vuelos_disponibles) == 1
    assert vuelos_disponibles[0].id == 301
    assert vuelos_disponibles[0].asientos_disponibles > 0


def test_vuelos_disponibles_ninguno(db_session, create_vuelo):
    """
    Verifica que vuelos_disponibles() devuelva lista vacía si todos están llenos.
    """
    salida = datetime.utcnow() + timedelta(days=5)
    vuelo_lleno = {
        "id": 303,
        "origen": "Ibagué (IBG)",
        "destino": "San Andrés (ADZ)",
        "salida": salida,
        "llegada": salida + timedelta(hours=3),
        "duracion": 3.0,
        "precio_base": 400000.0,
        "asientos_disponibles": 0
    }
    
    create_vuelo(vuelo_lleno)
    
    vuelos_disponibles = vuelo_service.vuelos_disponibles(db_session)
    
    assert vuelos_disponibles == []


# ========== PRUEBAS DE ACTUALIZACIÓN ==========

def test_actualizar_vuelo_exitoso(db_session, create_vuelo, vuelo_data):
    """
    Verifica que se pueda actualizar un vuelo correctamente.
    """
    vuelo = create_vuelo(vuelo_data)
    
    # Actualizar datos
    nuevos_datos = VueloUpdate(
        id=vuelo.id,
        origen=vuelo.origen,
        destino=vuelo.destino,
        salida=vuelo.salida,
        llegada=vuelo.llegada,
        duracion=vuelo.duracion,
        precio_base=180000.0,  # Precio actualizado
        asientos_disponibles=30  # Asientos actualizados
    )
    
    vuelo_actualizado = vuelo_service.actualizar_vuelo(db_session, vuelo.id, nuevos_datos)
    
    assert vuelo_actualizado.precio_base == 180000.0
    assert vuelo_actualizado.asientos_disponibles == 30


def test_actualizar_vuelo_inexistente(db_session):
    """
    Verifica que actualizar un vuelo inexistente lance excepción.
    
    Debe lanzar HTTPException con código 404.
    """
    salida = datetime.utcnow() + timedelta(days=10)
    datos = VueloUpdate(
        id=9999,
        origen="Test",
        destino="Test",
        salida=salida,
        llegada=salida + timedelta(hours=1),
        duracion=1.0,
        precio_base=100000.0,
        asientos_disponibles=50
    )
    
    with pytest.raises(HTTPException) as exc_info:
        vuelo_service.actualizar_vuelo(db_session, 9999, datos)
    
    assert exc_info.value.status_code == 404


# ========== PRUEBAS DE ELIMINACIÓN ==========

def test_eliminar_vuelo_existente(db_session, create_vuelo, vuelo_data):
    """
    Verifica que se pueda eliminar un vuelo correctamente.
    """
    vuelo = create_vuelo(vuelo_data)
    
    resultado = vuelo_service.eliminar_vuelo(db_session, vuelo.id)
    
    assert "eliminado correctamente" in resultado["message"].lower()
    
    # Verificar que ya no existe
    with pytest.raises(HTTPException):
        vuelo_service.obtener_vuelo(db_session, vuelo.id)


def test_eliminar_vuelo_inexistente(db_session):
    """
    Verifica que eliminar un vuelo inexistente lance excepción.
    
    Debe lanzar HTTPException con código 404.
    """
    id_inexistente = 9999
    
    with pytest.raises(HTTPException) as exc_info:
        vuelo_service.eliminar_vuelo(db_session, id_inexistente)
    
    assert exc_info.value.status_code == 404


def test_eliminar_vuelo_con_reservas(db_session, create_vuelo, create_usuario, vuelo_data, usuario_cliente_data):
    """
    Verifica que al eliminar un vuelo, se eliminen sus reservas (cascade).
    """
    from app.models.reserva import Reserva
    
    vuelo = create_vuelo(vuelo_data)
    usuario = create_usuario(usuario_cliente_data)
    
    # Crear reserva asociada al vuelo
    reserva = Reserva(
        usuario_id=usuario.id,
        vuelo_id=vuelo.id,
        clase="económica",
        total=150000.0
    )
    db_session.add(reserva)
    db_session.commit()
    
    # Eliminar vuelo
    vuelo_service.eliminar_vuelo(db_session, vuelo.id)
    
    # Verificar que la reserva también se eliminó
    reservas = db_session.query(Reserva).filter(Reserva.vuelo_id == vuelo.id).all()
    assert len(reservas) == 0