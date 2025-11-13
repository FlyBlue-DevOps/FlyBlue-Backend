from sqlalchemy.orm import Session
from app.models.servicio import Servicio
from app.dto.servicio_dto import ServicioCreate, ServicioUpdate

def listar_servicios(db: Session):
    return db.query(Servicio).all()

def obtener_servicio(db: Session, servicio_id: int):
    return db.query(Servicio).filter(Servicio.id == servicio_id).first()

def crear_servicio(db: Session, datos: ServicioCreate):
    servicio = Servicio(**datos.dict())
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio

def actualizar_servicio(db: Session, servicio_id: int, datos: ServicioUpdate):
    servicio = obtener_servicio(db, servicio_id)
    if not servicio:
        return None

    for k, v in datos.dict(exclude_unset=True).items():
        setattr(servicio, k, v)

    db.commit()
    db.refresh(servicio)
    return servicio

def eliminar_servicio(db: Session, servicio_id: int):
    servicio = obtener_servicio(db, servicio_id)
    if not servicio:
        return None

    db.delete(servicio)
    db.commit()
    return servicio
