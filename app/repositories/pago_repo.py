from sqlalchemy.orm import Session
from app.models.reserva import Reserva
from app.models.pago import Pago
from app.dto.pago_dto import PagoCreate

def crear_pago(db: Session, datos: PagoCreate):
    pago = Pago(**datos.dict())
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago

def obtener_pago(db: Session, pago_id: int):
    return db.query(Pago).filter(Pago.id == pago_id).first()

def obtener_pago_por_reserva(db: Session, reserva_id: int):
    return db.query(Pago).filter(Pago.reserva_id == reserva_id).first()

def listar_pagos_por_usuario(db: Session, usuario_id: int):
    return (
        db.query(Pago)
        .join(Pago.reserva)
        .filter(Reserva.usuario_id == usuario_id)
        .all()
    )
