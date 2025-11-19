from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import servicio_repo
from app.dto.servicio_dto import ServicioCreate, ServicioUpdate

def listar_servicios(db: Session):
    return servicio_repo.listar_servicios(db)

def obtener_servicio(db: Session, servicio_id: int):
    servicio = servicio_repo.obtener_servicio(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

def crear_servicio(db: Session, datos: ServicioCreate):
    # 1) Verificar si ya existe un servicio con ese nombre
    existente = db.query(servicio_repo.Servicio).filter(
        servicio_repo.Servicio.nombre == datos.nombre
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un servicio con este nombre"
        )

    # 2) Crear el servicio normalmente
    return servicio_repo.crear_servicio(db, datos)

def actualizar_servicio(db: Session, servicio_id: int, datos: ServicioUpdate):
    servicio = servicio_repo.actualizar_servicio(db, servicio_id, datos)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

def eliminar_servicio(db: Session, servicio_id: int):
    servicio = servicio_repo.eliminar_servicio(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": f"Servicio {servicio_id} eliminado correctamente"}
