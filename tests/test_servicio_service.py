# tests/test_servicio_service.py
"""
Pruebas unitarias para el servicio de servicios adicionales (services/servicio_service.py).

Valida:
- Creación de servicios
- Obtención por ID
- Listado general
- Actualización de campos
- Eliminación lógica/física (según la implementación)
"""

import pytest
from fastapi import HTTPException

from app.services import servicio_service
from app.dto.servicio_dto import ServicioCreate, ServicioUpdate
from app.models.servicio import Servicio


# ========== PRUEBAS DE CREACIÓN ==========

def test_crear_servicio_exitoso(db_session):
    """
    Verifica que se pueda crear un servicio sin errores.
    """
    datos = ServicioCreate(
        nombre="Internet a bordo",
        descripcion="Wifi satelital durante el vuelo",
        precio=25000.0
    )

    servicio = servicio_service.crear_servicio(db_session, datos)

    assert servicio is not None
    assert servicio.nombre == "Internet a bordo"
    assert servicio.descripcion == "Wifi satelital durante el vuelo"
    assert servicio.precio == 25000.0


def test_crear_servicio_nombre_repetido(db_session, create_servicio):
    """
    Verifica que no se pueda crear un servicio con un nombre ya existente.
    Debe lanzar HTTPException con código 400.
    """
    create_servicio({
        "nombre": "Comida Premium",
        "descripcion": "Menú especial",
        "precio": 50000.0
    })

    datos = ServicioCreate(
        nombre="Comida Premium",
        descripcion="Menu duplicado",
        precio=45000.0
    )

    with pytest.raises(HTTPException) as exc_info:
        servicio_service.crear_servicio(db_session, datos)

    assert exc_info.value.status_code == 400
    assert "ya existe" in exc_info.value.detail.lower()


# ========== PRUEBAS DE LISTADO ==========

def test_listar_servicios(db_session, create_servicio):
    """
    Verifica que listar_servicios() retorne todos los servicios.
    """
    create_servicio({"nombre": "Wifi", "descripcion": "Internet", "precio": 20000})
    create_servicio({"nombre": "Bebidas", "descripcion": "Jugos y café", "precio": 15000})

    servicios = servicio_service.listar_servicios(db_session)

    assert len(servicios) >= 2
    assert any(s.nombre == "Wifi" for s in servicios)
    assert any(s.nombre == "Bebidas" for s in servicios)


# ========== PRUEBAS DE OBTENCIÓN POR ID ==========

def test_obtener_servicio_existente(db_session, create_servicio):
    """
    Verifica que obtener_servicio() retorne el servicio cuando existe.
    """
    servicio = create_servicio({
        "nombre": "Manta térmica",
        "descripcion": "Para vuelos fríos",
        "precio": 12000.0
    })

    obtenido = servicio_service.obtener_servicio(db_session, servicio.id)

    assert obtenido.id == servicio.id
    assert obtenido.nombre == "Manta térmica"


def test_obtener_servicio_inexistente(db_session):
    """
    Verifica que obtener_servicio() lance excepción si el ID no existe.
    """
    with pytest.raises(HTTPException) as exc_info:
        servicio_service.obtener_servicio(db_session, 99999)

    assert exc_info.value.status_code == 404
    assert "no encontrado" in exc_info.value.detail.lower()


# ========== PRUEBAS DE ACTUALIZACIÓN ==========

def test_actualizar_servicio_exitoso(db_session, create_servicio):
    """
    Verifica que se pueda actualizar nombre, descripción y precio de un servicio.
    """
    servicio = create_servicio({
        "nombre": "Snacks",
        "descripcion": "Galletas y papas",
        "precio": 10000.0
    })

    actualizacion = ServicioUpdate(
        nombre="Snacks Premium",
        descripcion="Papas, galletas y chocolates",
        precio=18000.0
    )

    actualizado = servicio_service.actualizar_servicio(db_session, servicio.id, actualizacion)

    assert actualizado.nombre == "Snacks Premium"
    assert actualizado.descripcion == "Papas, galletas y chocolates"
    assert actualizado.precio == 18000.0


def test_actualizar_servicio_inexistente(db_session):
    """
    Verifica que actualizar un servicio inexistente lance excepción.
    """
    with pytest.raises(HTTPException) as exc_info:
        servicio_service.actualizar_servicio(
            db_session,
            99999,
            ServicioUpdate(nombre="Test")
        )

    assert exc_info.value.status_code == 404


# ========== PRUEBAS DE ELIMINACIÓN ==========

def test_eliminar_servicio_exitoso(db_session, create_servicio):
    """
    Verifica que eliminar_servicio() borre el servicio correctamente.
    """
    servicio = create_servicio({
        "nombre": "Entretenimiento",
        "descripcion": "Películas y música",
        "precio": 30000.0
    })

    servicio_service.eliminar_servicio(db_session, servicio.id)

    with pytest.raises(HTTPException):
        servicio_service.obtener_servicio(db_session, servicio.id)


def test_eliminar_servicio_inexistente(db_session):
    """
    Verifica que eliminar un servicio inexistente lance excepción.
    """
    with pytest.raises(HTTPException) as exc_info:
        servicio_service.eliminar_servicio(db_session, 99999)

    assert exc_info.value.status_code == 404
