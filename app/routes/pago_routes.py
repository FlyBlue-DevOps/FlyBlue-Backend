from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import pago_service
from app.dto.pago_dto import PagoCreate, PagoRead
from app.core.auth import get_current_user, require_admin
from app.models.usuario import Usuario

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/", response_model=PagoRead)
def crear_pago(
    datos: PagoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return pago_service.crear_pago(db, datos, current_user)


@router.get("/{id}", response_model=PagoRead)
def obtener_pago(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return pago_service.obtener_pago(db, id, current_user)


@router.get("/reserva/{id}", response_model=PagoRead)
def obtener_pago_de_reserva(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return pago_service.obtener_pago_de_reserva(db, id, current_user)


@router.get("/usuario/{id}", response_model=list[PagoRead])
def listar_pagos_usuario(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    return pago_service.listar_pagos_usuario(db, id)
