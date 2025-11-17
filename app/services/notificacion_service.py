from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import notificacion_repo
from app.dto.notificacion_dto import NotificacionCreate
from app.models.usuario import Usuario


def listar_notificaciones(db: Session, current_user: Usuario):
    return notificacion_repo.listar_notificaciones(db, current_user.id)


def listar_no_leidas(db: Session, current_user: Usuario):
    return notificacion_repo.listar_no_leidas(db, current_user.id)


def obtener_notificacion(db: Session, notificacion_id: int, current_user: Usuario):
    notif = notificacion_repo.obtener_notificacion(db, notificacion_id)

    if not notif or notif.usuario_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    return notif


def crear_notificacion(db: Session, datos: NotificacionCreate):
    return notificacion_repo.crear_notificacion(db, datos)


def marcar_leida(db: Session, notificacion_id: int, current_user: Usuario):
    notif = notificacion_repo.marcar_leida(db, notificacion_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return notif


def eliminar_notificacion(db: Session, notificacion_id: int, current_user: Usuario):
    eliminado = notificacion_repo.eliminar_notificacion(db, notificacion_id, current_user.id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    return {"message": "Notificación eliminada correctamente"}
