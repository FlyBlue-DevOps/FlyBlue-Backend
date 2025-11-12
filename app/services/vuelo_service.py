from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import vuelo_repo
from app.dto.vuelo_dto import VueloCreate, VueloUpdate

def listar_vuelos(db: Session):
    return vuelo_repo.listar_vuelos(db)

def obtener_vuelo(db: Session, vuelo_id: int):
    vuelo = vuelo_repo.obtener_vuelo(db, vuelo_id)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

def vuelos_disponibles(db: Session):
    return vuelo_repo.buscar_vuelos_disponibles(db)

def crear_vuelo(db: Session, datos: VueloCreate):
    existente = db.query(vuelo_repo.Vuelo).filter(vuelo_repo.Vuelo.id == datos.id).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un vuelo con este código.")
    return vuelo_repo.crear_vuelo(db, datos)

def actualizar_vuelo(db: Session, vuelo_id: int, datos: VueloUpdate):
    vuelo = vuelo_repo.actualizar_vuelo(db, vuelo_id, datos)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

def eliminar_vuelo(db: Session, vuelo_id: int):
    vuelo = vuelo_repo.eliminar_vuelo(db, vuelo_id)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return {"message": f"Vuelo con id {vuelo_id} eliminado correctamente"}
