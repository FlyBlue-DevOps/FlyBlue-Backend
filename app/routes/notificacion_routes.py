from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user, require_admin
from app.dto.notificacion_dto import NotificacionCreate, NotificacionRead
from app.models.usuario import Usuario
from app.services import notificacion_service

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

# === GET /notificaciones/ ===
@router.get("/", response_model=list[NotificacionRead])
def listar_notificaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return notificacion_service.listar_notificaciones(db, current_user)

# === GET /notificaciones/nuevas ===
@router.get("/nuevas", response_model=list[NotificacionRead])
def listar_no_leidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return notificacion_service.listar_no_leidas(db, current_user)

# === GET /notificaciones/{id} ===
@router.get("/{id}", response_model=NotificacionRead)
def obtener_notificacion(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return notificacion_service.obtener_notificacion(db, id, current_user)

# === POST /notificaciones/ === (solo admin / sistema)
@router.post("/", response_model=NotificacionRead)
def crear_notificacion(
    datos: NotificacionCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return notificacion_service.crear_notificacion(db, datos)

# === PUT /notificaciones/{id} ===
@router.put("/{id}", response_model=NotificacionRead)
def marcar_notificacion_como_leida(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return notificacion_service.marcar_leida(db, id, current_user)

# === DELETE /notificaciones/{id} ===
@router.delete("/{id}")
def eliminar_notificacion(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return notificacion_service.eliminar_notificacion(db, id, current_user)
