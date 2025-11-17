# tests/test_reserva_service.py
"""
Pruebas unitarias para el servicio de reservas (services/reserva_service.py).

⚠️ COMPONENTE CRÍTICO: Las reservas tienen lógica acoplada con vuelos.

Valida:
- Creación de reservas y decremento de asientos disponibles
- Validación de vuelo existente antes de reservar
- Validación de disponibilidad de asientos
- Listado de reservas (por usuario y admin)
- Actualización de reservas
- Confirmación de reservas (solo admin)
- Eliminación de reservas y restauración de asientos
"""

import pytest
from fastapi import HTTPException

from app.services import reserva_service
from app.dto.reserva_dto import ReservaCreate, ReservaUpdate
from app.models.vuelo import Vuelo
from app.models.reserva import Reserva


# ========== PRUEBAS DE CREACIÓN (CON LÓGICA DE ASIENTOS) ==========

def test_crear_reserva_exitosa(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que se pueda crear una reserva y que los asientos disminuyan.
    
    ⚠️ CRÍTICO: Valida que al crear una reserva, los asientos_disponibles del vuelo
    se decrementan automáticamente.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    asientos_iniciales = vuelo.asientos_disponibles
    
    # Crear reserva
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    # Verificaciones de la reserva
    assert reserva is not None
    assert reserva.usuario_id == usuario.id
    assert reserva.vuelo_id == vuelo.id
    assert reserva.clase == "económica"
    assert reserva.asiento == "12A"
    assert reserva.total == 150000.0
    assert reserva.estado == "pendiente"  # Estado por defecto
    
    # ⚠️ VERIFICACIÓN CRÍTICA: Los asientos deben haber disminuido
    db_session.refresh(vuelo)
    assert vuelo.asientos_disponibles == asientos_iniciales - 1


def test_crear_reserva_vuelo_inexistente(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que no se pueda crear reserva para un vuelo que no existe.
    
    Debe lanzar HTTPException con código 404.
    """
    usuario = create_usuario(usuario_cliente_data)
    
    datos = ReservaCreate(
        vuelo_id=99999,  # Vuelo inexistente
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    
    with pytest.raises(HTTPException) as exc_info:
        reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    assert exc_info.value.status_code == 404
    assert "vuelo no encontrado" in exc_info.value.detail.lower()


def test_crear_reserva_sin_asientos_disponibles(db_session, create_usuario, create_vuelo, usuario_cliente_data):
    """
    Verifica que no se pueda crear reserva cuando el vuelo no tiene asientos.
    
    Debe lanzar HTTPException con código 400.
    """
    from datetime import datetime, timedelta
    
    usuario = create_usuario(usuario_cliente_data)
    
    # Crear vuelo SIN asientos
    salida = datetime.utcnow() + timedelta(days=10)
    vuelo_lleno_data = {
        "id": 500,
        "origen": "Ibagué (IBG)",
        "destino": "Medellín (MDE)",
        "salida": salida,
        "llegada": salida + timedelta(hours=2),
        "duracion": 2.0,
        "precio_base": 150000.0,
        "asientos_disponibles": 0  # VUELO LLENO
    }
    vuelo = create_vuelo(vuelo_lleno_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    
    with pytest.raises(HTTPException) as exc_info:
        reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    assert exc_info.value.status_code == 400
    assert "no hay asientos disponibles" in exc_info.value.detail.lower()


def test_crear_multiples_reservas_mismo_vuelo(db_session, create_usuario, create_vuelo, vuelo_data):
    """
    Verifica que se puedan crear múltiples reservas para el mismo vuelo
    y que los asientos se decrementan correctamente cada vez.
    """
    # Crear dos usuarios
    usuario1_data = {
        "id": 11111111,
        "nombre": "Usuario 1",
        "email": "usuario1@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    usuario2_data = {
        "id": 22222222,
        "nombre": "Usuario 2",
        "email": "usuario2@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    
    usuario1 = create_usuario(usuario1_data)
    usuario2 = create_usuario(usuario2_data)
    vuelo = create_vuelo(vuelo_data)
    
    asientos_iniciales = vuelo.asientos_disponibles
    
    # Primera reserva
    datos1 = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva_service.crear_reserva(db_session, datos1, usuario1.id)
    
    # Segunda reserva
    datos2 = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="ejecutiva",
        asiento="1B",
        total=300000.0
    )
    reserva_service.crear_reserva(db_session, datos2, usuario2.id)
    
    # Verificar asientos
    db_session.refresh(vuelo)
    assert vuelo.asientos_disponibles == asientos_iniciales - 2


# ========== PRUEBAS DE LISTADO ==========

def test_listar_reservas_como_admin(db_session, create_usuario, create_vuelo, usuario_admin_data, usuario_cliente_data, vuelo_data):
    """
    Verifica que un admin pueda ver todas las reservas del sistema.
    """
    admin = create_usuario(usuario_admin_data)
    cliente = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    # Crear reserva del cliente
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva_service.crear_reserva(db_session, datos, cliente.id)
    
    # Admin lista todas las reservas (sin filtro de usuario_id)
    reservas = reserva_service.listar_reservas(db_session)
    
    assert len(reservas) >= 1
    assert any(r.usuario_id == cliente.id for r in reservas)


def test_listar_reservas_como_cliente(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que un cliente solo vea sus propias reservas.
    """
    # Crear dos clientes
    cliente1_data = usuario_cliente_data
    cliente2_data = {
        "id": 99999999,
        "nombre": "Otro Cliente",
        "email": "otro@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    
    cliente1 = create_usuario(cliente1_data)
    cliente2 = create_usuario(cliente2_data)
    vuelo = create_vuelo(vuelo_data)
    
    # Cada cliente crea una reserva
    datos1 = ReservaCreate(vuelo_id=vuelo.id, clase="económica", asiento="12A", total=150000.0)
    datos2 = ReservaCreate(vuelo_id=vuelo.id, clase="ejecutiva", asiento="1B", total=300000.0)
    
    reserva_service.crear_reserva(db_session, datos1, cliente1.id)
    reserva_service.crear_reserva(db_session, datos2, cliente2.id)
    
    # Cliente1 lista solo sus reservas
    reservas_cliente1 = reserva_service.listar_reservas(db_session, usuario_id=cliente1.id)
    
    assert len(reservas_cliente1) == 1
    assert reservas_cliente1[0].usuario_id == cliente1.id


# ========== PRUEBAS DE OBTENCIÓN POR ID ==========

def test_obtener_reserva_existente(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que se pueda obtener una reserva por su ID.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva_creada = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    reserva = reserva_service.obtener_reserva(db_session, reserva_creada.id, usuario)
    
    assert reserva is not None
    assert reserva.id == reserva_creada.id
    assert reserva.usuario_id == usuario.id


def test_obtener_reserva_inexistente(db_session):
    """
    Verifica que obtener_reserva() lance excepción cuando el ID no existe.
    
    Debe lanzar HTTPException con código 404.
    """
    with pytest.raises(HTTPException) as exc_info:
        fake_user = type("User", (), {"rol": "admin"})()
        reserva_service.obtener_reserva(db_session, 99999, fake_user)

    
    assert exc_info.value.status_code == 404
    assert "no encontrada" in exc_info.value.detail.lower()


# ========== PRUEBAS DE ACTUALIZACIÓN ==========

def test_actualizar_reserva_estado(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que se pueda actualizar el estado de una reserva.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    # Actualizar estado
    actualizacion = ReservaUpdate(estado="confirmada")
    reserva_actualizada = reserva_service.actualizar_reserva(db_session, reserva.id, actualizacion, usuario)
    
    assert reserva_actualizada.estado == "confirmada"


def test_actualizar_reserva_clase_y_asiento(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que se pueda actualizar la clase y asiento de una reserva.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    # Actualizar clase y asiento
    actualizacion = ReservaUpdate(
        clase="ejecutiva",
        asiento="1B"
    )
    reserva_actualizada = reserva_service.actualizar_reserva(db_session, reserva.id, actualizacion, usuario)
    
    assert reserva_actualizada.clase == "ejecutiva"
    assert reserva_actualizada.asiento == "1B"


# ========== PRUEBAS DE CONFIRMACIÓN (SOLO ADMIN) ==========

def test_confirmar_reserva_pendiente(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que se pueda confirmar una reserva pendiente.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    assert reserva.estado == "pendiente"
    
    # Confirmar reserva
    reserva_confirmada = reserva_service.confirmar_reserva(db_session, reserva.id)
    
    assert reserva_confirmada.estado == "confirmada"


def test_confirmar_reserva_ya_confirmada(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que no se pueda confirmar una reserva que ya está confirmada.
    
    Debe lanzar HTTPException con código 400.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    # Confirmar por primera vez
    reserva_service.confirmar_reserva(db_session, reserva.id)
    
    # Intentar confirmar nuevamente
    with pytest.raises(HTTPException) as exc_info:
        reserva_service.confirmar_reserva(db_session, reserva.id)
    
    assert exc_info.value.status_code == 400
    assert "ya está confirmada" in exc_info.value.detail.lower()


# ========== PRUEBAS DE ELIMINACIÓN (CON RESTAURACIÓN DE ASIENTOS) ==========

def test_eliminar_reserva_restaura_asientos(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    ⚠️ CRÍTICO: Verifica que al eliminar una reserva, los asientos del vuelo
    se incrementen nuevamente.
    """
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    asientos_iniciales = vuelo.asientos_disponibles
    
    # Crear reserva (decrementa asientos)
    datos = ReservaCreate(
        vuelo_id=vuelo.id,
        clase="económica",
        asiento="12A",
        total=150000.0
    )
    reserva = reserva_service.crear_reserva(db_session, datos, usuario.id)
    
    db_session.refresh(vuelo)
    asientos_despues_reserva = vuelo.asientos_disponibles
    assert asientos_despues_reserva == asientos_iniciales - 1
    
    # Eliminar reserva (debe restaurar asientos)
    reserva_service.eliminar_reserva(db_session, reserva.id, usuario)
    
    db_session.refresh(vuelo)
    assert vuelo.asientos_disponibles == asientos_iniciales  # Asientos restaurados


def test_eliminar_reserva_inexistente(db_session):
    """
    Verifica que eliminar una reserva inexistente lance excepción.
    
    Debe lanzar HTTPException con código 404.
    """
    with pytest.raises(HTTPException) as exc_info:
        fake_user = type("User", (), {"rol": "admin"})()
        reserva_service.eliminar_reserva(db_session, 99999, fake_user)

    
    assert exc_info.value.status_code == 404
    assert "no encontrada" in exc_info.value.detail.lower()


def test_eliminar_multiples_reservas_restaura_correctamente(db_session, create_usuario, create_vuelo, vuelo_data):
    """
    Verifica que eliminar múltiples reservas restaure correctamente todos los asientos.
    """
    # Crear dos usuarios
    usuario1_data = {
        "id": 11111111,
        "nombre": "Usuario 1",
        "email": "usuario1@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    usuario2_data = {
        "id": 22222222,
        "nombre": "Usuario 2",
        "email": "usuario2@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    
    usuario1 = create_usuario(usuario1_data)
    usuario2 = create_usuario(usuario2_data)
    vuelo = create_vuelo(vuelo_data)
    
    asientos_iniciales = vuelo.asientos_disponibles
    
    # Crear dos reservas
    datos1 = ReservaCreate(vuelo_id=vuelo.id, clase="económica", asiento="12A", total=150000.0)
    datos2 = ReservaCreate(vuelo_id=vuelo.id, clase="ejecutiva", asiento="1B", total=300000.0)
    
    reserva1 = reserva_service.crear_reserva(db_session, datos1, usuario1.id)
    reserva2 = reserva_service.crear_reserva(db_session, datos2, usuario2.id)
    
    db_session.refresh(vuelo)
    assert vuelo.asientos_disponibles == asientos_iniciales - 2
    
    # Eliminar ambas reservas
    reserva_service.eliminar_reserva(db_session, reserva1.id, usuario1)
    reserva_service.eliminar_reserva(db_session, reserva2.id, usuario2)
    
    db_session.refresh(vuelo)
    assert vuelo.asientos_disponibles == asientos_iniciales  # Todos los asientos restaurados