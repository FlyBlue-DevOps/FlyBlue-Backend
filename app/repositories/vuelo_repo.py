from sqlalchemy.orm import Session
from app.models.vuelo import Vuelo
from app.dto.vuelo_dto import VueloCreate, VueloUpdate

def listar_vuelos(db: Session):
    return db.query(Vuelo).all()

def obtener_vuelo(db: Session, vuelo_id: int):
    return db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()

def buscar_vuelos_disponibles(db: Session):
    return db.query(Vuelo).filter(Vuelo.asientos_disponibles > 0).all()

def crear_vuelo(db: Session, datos: VueloCreate):
    nuevo_vuelo = Vuelo(**datos.dict())
    db.add(nuevo_vuelo)
    db.commit()
    db.refresh(nuevo_vuelo)
    return nuevo_vuelo

def actualizar_vuelo(db: Session, vuelo_id: int, datos: VueloUpdate):
    vuelo = obtener_vuelo(db, vuelo_id)
    if not vuelo:
        return None
    for key, value in datos.dict().items():
        setattr(vuelo, key, value)
    db.commit()
    db.refresh(vuelo)
    return vuelo

def eliminar_vuelo(db: Session, vuelo_id: int):
    vuelo = obtener_vuelo(db, vuelo_id)
    if not vuelo:
        return None
    db.delete(vuelo)
    db.commit()
    return vuelo
