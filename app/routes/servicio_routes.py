from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import require_admin
from app.services import servicio_service
from app.dto.servicio_dto import ServicioCreate, ServicioUpdate, ServicioRead

router = APIRouter(prefix="/servicios", tags=["Servicios"])

# === GET /servicios/ ===
@router.get("/", response_model=list[ServicioRead])
def listar_servicios(db: Session = Depends(get_db),):
    return servicio_service.listar_servicios(db)

# === GET /servicios/{id} ===
@router.get("/{id}", response_model=ServicioRead)
def obtener_servicio(id: int, db: Session = Depends(get_db)):
    return servicio_service.obtener_servicio(db, id)

# === POST /servicios/ === (solo admin)
@router.post("/", response_model=ServicioRead, status_code=status.HTTP_201_CREATED)
def crear_servicio(
    datos: ServicioCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return servicio_service.crear_servicio(db, datos)

# === PUT /servicios/{id} === (solo admin)
@router.put("/{id}", response_model=ServicioRead)
def actualizar_servicio(
    id: int,
    datos: ServicioUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return servicio_service.actualizar_servicio(db, id, datos)

# === DELETE /servicios/{id} === (solo admin)
@router.delete("/{id}")
def eliminar_servicio(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return servicio_service.eliminar_servicio(db, id)
