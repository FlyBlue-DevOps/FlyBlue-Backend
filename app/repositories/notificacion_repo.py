from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion
from app.dto.notificacion_dto import NotificacionCreate

def listar_notificaciones(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(
        Notificacion.usuario_id == usuario_id
    ).order_by(Notificacion.fecha.desc()).all()

def listar_no_leidas(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(
        Notificacion.usuario_id == usuario_id,
        Notificacion.leido == False
    ).order_by(Notificacion.fecha.desc()).all()

def obtener_notificacion(db: Session, notificacion_id: int):
    return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()

def crear_notificacion(db: Session, datos: NotificacionCreate):
    nueva = Notificacion(**datos.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def marcar_leida(db: Session, notificacion_id: int, usuario_id: int):
    notif = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.usuario_id == usuario_id
    ).first()

    if not notif:
        return None

    notif.leido = True
    db.commit()
    db.refresh(notif)
    return notif

def eliminar_notificacion(db: Session, notificacion_id: int, usuario_id: int):
    notif = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.usuario_id == usuario_id
    ).first()

    if not notif:
        return None

    db.delete(notif)
    db.commit()
    return True
