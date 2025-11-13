from sqlalchemy.orm import Session
from app.models.reserva import Reserva
from app.dto.reserva_dto import ReservaCreate, ReservaUpdate

def listar_reservas(db: Session, usuario_id: int = None):
    if usuario_id:
        return db.query(Reserva).filter(Reserva.usuario_id == usuario_id).all()
    return db.query(Reserva).all()

def obtener_reserva(db: Session, reserva_id: int):
    return db.query(Reserva).filter(Reserva.id == reserva_id).first()

def crear_reserva(db: Session, datos: ReservaCreate, usuario_id: int):
    nueva = Reserva(usuario_id=usuario_id, **datos.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def actualizar_reserva(db: Session, reserva_id: int, datos: ReservaUpdate):
    reserva = obtener_reserva(db, reserva_id)
    if not reserva:
        return None
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(reserva, k, v)
    db.commit()
    db.refresh(reserva)
    return reserva

def eliminar_reserva(db: Session, reserva_id: int):
    reserva = obtener_reserva(db, reserva_id)
    
    if not reserva:
        return None
        
    db.delete(reserva)
    db.commit()
    return reserva
