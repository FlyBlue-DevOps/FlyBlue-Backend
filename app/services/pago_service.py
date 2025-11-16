from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import pago_repo, reserva_repo
from app.dto.pago_dto import PagoCreate
from app.models.usuario import Usuario

def crear_pago(db: Session, datos: PagoCreate, current_user: Usuario):
    reserva = reserva_repo.obtener_reserva(db, datos.reserva_id)
    if not reserva:
        raise HTTPException(404, "Reserva no encontrada")

    # Validar dueño
    if reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(403, "No autorizado")

    # Evitar pagos duplicados
    existente = pago_repo.obtener_pago_por_reserva(db, datos.reserva_id)
    if existente:
        raise HTTPException(400, "La reserva ya tiene un pago registrado")

    # Pago simulado: generar referencia falsa
    datos_dict = datos.dict()
    datos_dict["referencia"] = f"PAY-{reserva.id}-{current_user.id}"

    pago = pago_repo.crear_pago(db, datos)
    return pago


def obtener_pago(db: Session, pago_id: int, current_user: Usuario):
    pago = pago_repo.obtener_pago(db, pago_id)
    if not pago:
        raise HTTPException(404, "Pago no encontrado")

    if pago.reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(403, "No autorizado")

    return pago


def obtener_pago_de_reserva(db: Session, reserva_id: int, current_user: Usuario):
    pago = pago_repo.obtener_pago_por_reserva(db, reserva_id)
    if not pago:
        raise HTTPException(404, "No existe un pago para esta reserva")

    if pago.reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(403, "No autorizado")

    return pago


def listar_pagos_usuario(db: Session, usuario_id: int):
    return pago_repo.listar_pagos_por_usuario(db, usuario_id)
