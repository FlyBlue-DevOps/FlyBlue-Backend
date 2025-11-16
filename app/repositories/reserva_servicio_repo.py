from sqlalchemy.orm import Session
from app.models.reserva_servicio import ReservaServicio
from app.models.servicio import Servicio
from app.repositories import reserva_repo

def agregar_servicio(db: Session, reserva_id: int, servicio_id: int, cantidad: int):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        return None

    subtotal = float(servicio.precio) * cantidad

    nuevo = ReservaServicio(
        reserva_id=reserva_id,
        servicio_id=servicio_id,
        cantidad=cantidad,
        subtotal=subtotal
    )
    
        
    

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def obtener_servicios_de_reserva(db: Session, reserva_id: int):
    return db.query(ReservaServicio).filter(ReservaServicio.reserva_id == reserva_id).all()


