# tests/test_notificacion_service.py
"""
Pruebas unitarias para el servicio de notificaciones (services/notificacion_service.py).

Valida:
- Envío de notificaciones (creación)
- Listado general
- Obtención por ID
"""

import pytest
from fastapi import HTTPException

from app.services import notificacion_service
from app.dto.notificacion_dto import NotificacionCreate
from app.models.notificacion import Notificacion
from types import SimpleNamespace



# ========== PRUEBAS DE CREACIÓN ==========

def test_enviar_notificacion_exitoso(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que se pueda enviar una notificación correctamente.
    """
    usuario = create_usuario(usuario_cliente_data)

    datos = NotificacionCreate(
        usuario_id=usuario.id,
        titulo="Pago aprobado",
        mensaje="Tu pago fue aprobado correctamente."
    )

    notificacion = notificacion_service.crear_notificacion(db_session, datos)

    assert notificacion is not None
    assert notificacion.usuario_id == usuario.id
    assert notificacion.titulo == "Pago aprobado"
    assert notificacion.mensaje == "Tu pago fue aprobado correctamente."


def test_enviar_notificacion_usuario_inexistente(db_session):
    """
    Verifica que no se pueda enviar notificación a un usuario inexistente.
    """
    datos = NotificacionCreate(
        usuario_id=99999,
        titulo="Test",
        mensaje="Mensaje"
    )

    with pytest.raises(HTTPException) as exc_info:
        notificacion_service.crear_notificacion(db_session, datos)

    assert exc_info.value.status_code == 404
    assert "usuario no encontrado" in exc_info.value.detail.lower()


# ========== PRUEBAS DE LISTADO ==========

def test_listar_notificaciones(db_session, create_notificacion):
    """
    Verifica que listar_notificaciones() retorne todas las notificaciones.
    """
    # Creamos dos notificaciones
    create_notificacion({"usuario_id": 1, "titulo": "A", "mensaje": "X"})
    create_notificacion({"usuario_id": 2, "titulo": "B", "mensaje": "Y"})

    # Usuario fake requerido por el servicio
    fake_user = SimpleNamespace(id=1, rol="cliente")

    # Llamar al servicio con current_user
    notifs = notificacion_service.listar_notificaciones(db_session, fake_user)

    # Debe traer solo las notificaciones del usuario 1
    assert len(notifs) == 1
    assert all(n.usuario_id == 1 for n in notifs)


# ========== PRUEBAS DE OBTENCIÓN ==========

def test_obtener_notificacion_existente(db_session, create_notificacion):
    """
    Verifica que obtener_notificacion() devuelva la notificación existente.
    """
    notif = create_notificacion({
        "usuario_id": 1,
        "titulo": "Recordatorio",
        "mensaje": "Tu vuelo sale mañana."
    })
    fake_user = SimpleNamespace(id=1, rol="cliente")

    obtenido = notificacion_service.obtener_notificacion(db_session, notif.id, fake_user)

    assert obtenido.id == notif.id
    assert obtenido.titulo == "Recordatorio"


def test_obtener_notificacion_inexistente(db_session):
    """
    Verifica que obtener_notificacion() lance excepción si el ID no existe.
    """
    fake_user = SimpleNamespace(id=1, rol="cliente")
    with pytest.raises(HTTPException) as exc_info:
        notificacion_service.obtener_notificacion(db_session, 99999, fake_user)

    assert exc_info.value.status_code == 404
    assert "no encontrada" in exc_info.value.detail.lower()
