from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import reserva_repo
from app.models.vuelo import Vuelo
from app.dto.reserva_dto import ReservaCreate, ReservaUpdate

def listar_reservas(db: Session, usuario_id: int = None):
    return reserva_repo.listar_reservas(db, usuario_id)

def obtener_reserva(db: Session, reserva_id: int):
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

def crear_reserva(db: Session, datos: ReservaCreate, usuario_id: int):
    vuelo = db.query(Vuelo).filter(Vuelo.id == datos.vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    if vuelo.asientos_disponibles <= 0:
        raise HTTPException(status_code=400, detail="No hay asientos disponibles")

    # Crear reserva
    nueva = reserva_repo.crear_reserva(db, datos, usuario_id)

    # Actualizar asientos del vuelo
    vuelo.asientos_disponibles -= 1
    db.commit()
    return nueva

def actualizar_reserva(db: Session, reserva_id: int, datos: ReservaUpdate):
    reserva = reserva_repo.actualizar_reserva(db, reserva_id, datos)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

def confirmar_reserva(db: Session, reserva_id: int):
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if reserva.estado == "confirmada":
        raise HTTPException(status_code=400, detail="La reserva ya está confirmada")

    reserva.estado = "confirmada"
    db.commit()
    db.refresh(reserva)
    return reserva

def eliminar_reserva(db: Session, reserva_id: int):
    
    reserva = reserva_repo.eliminar_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return {"message": f"Reserva {reserva_id} eliminada correctamente"}
