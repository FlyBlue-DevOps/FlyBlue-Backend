# tests/test_pago_service.py
"""
Pruebas unitarias para PagoService.

Este archivo valida:
- Creación de pagos
- Obtención de pagos
- Listado de pagos
- Manejo de errores y restricciones
"""
import pytest
from types import SimpleNamespace
from app.services import pago_service
from app.dto.pago_dto import PagoCreate


# ==========================================================
# FIXTURE: Crea usuario + vuelo + reserva
# ==========================================================
@pytest.fixture
def reserva_preparada(create_usuario, create_vuelo, create_reserva, usuario_cliente_data, vuelo_data):
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)

    reserva = create_reserva({
        "usuario_id": usuario.id,
        "vuelo_id": vuelo.id,
        "clase": "económica",
        "asiento": "12A",
        "total": 150000.0
    })

    return SimpleNamespace(usuario=usuario, reserva=reserva)


# ==========================================================
# TESTS
# ==========================================================

def test_crear_pago_exitoso(db_session, reserva_preparada):
    usuario = reserva_preparada.usuario
    reserva = reserva_preparada.reserva

    datos = PagoCreate(
        reserva_id=reserva.id,
        monto=100000,
        metodo="tarjeta"
    )

    pago = pago_service.crear_pago(db_session, datos, usuario)

    assert pago.id is not None
    assert pago.reserva_id == reserva.id
    assert pago.monto == 100000
    assert pago.metodo == "tarjeta"


def test_crear_pago_falla_por_reserva_inexistente(db_session):
    usuario_fake = SimpleNamespace(id=1, rol="cliente")

    datos = PagoCreate(
        reserva_id=9999,
        monto=100000,
        metodo="tarjeta"
    )

    with pytest.raises(Exception):
        pago_service.crear_pago(db_session, datos, usuario_fake)


def test_crear_pago_falla_por_pago_duplicado(db_session, reserva_preparada, create_pago):
    usuario = reserva_preparada.usuario
    reserva = reserva_preparada.reserva

    create_pago({
        "reserva_id": reserva.id,
        "monto": 50000,
        "metodo": "tarjeta",
        "estado": "completado"
    })

    datos = PagoCreate(
        reserva_id=reserva.id,
        monto=70000,
        metodo="tarjeta"
    )

    with pytest.raises(Exception):
        pago_service.crear_pago(db_session, datos, usuario)


def test_obtener_pago_exitoso(db_session, reserva_preparada, create_pago):
    usuario = reserva_preparada.usuario
    reserva = reserva_preparada.reserva

    pago = create_pago({
        "reserva_id": reserva.id,
        "monto": 90000,
        "metodo": "nequi",
        "estado": "completado"
    })

    resultado = pago_service.obtener_pago(db_session, pago.id, usuario)

    assert resultado.id == pago.id
    assert resultado.monto == 90000
    assert resultado.metodo == "nequi"


def test_obtener_pago_no_existente(db_session, reserva_preparada):
    usuario = reserva_preparada.usuario

    with pytest.raises(Exception):
        pago_service.obtener_pago(db_session, 9999, usuario)


def test_obtener_pago_de_reserva(db_session, reserva_preparada, create_pago):
    usuario = reserva_preparada.usuario
    reserva = reserva_preparada.reserva

    pago = create_pago({
        "reserva_id": reserva.id,
        "monto": 50000,
        "metodo": "tarjeta",
        "estado": "pendiente"
    })

    resultado = pago_service.obtener_pago_de_reserva(db_session, reserva.id, usuario)

    assert resultado.id == pago.id
    assert resultado.reserva_id == reserva.id


def test_listar_pagos_usuario(db_session, reserva_preparada, create_pago):
    usuario = reserva_preparada.usuario
    reserva = reserva_preparada.reserva

    create_pago({
        "reserva_id": reserva.id,
        "monto": 60000,
        "metodo": "tarjeta",
        "estado": "completado"
    })

    lista = pago_service.listar_pagos_usuario(db_session, usuario.id)

    assert len(lista) == 1
    assert lista[0].monto == 60000
