from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import require_admin
from app.services import vuelo_service
from app.dto.vuelo_dto import VueloRead, VueloCreate, VueloUpdate

router = APIRouter(prefix="/vuelos", tags=["Vuelos"])

# === GET /vuelos/ ===
@router.get("/", response_model=list[VueloRead])
def listar_vuelos(db: Session = Depends(get_db)):
    """Listar todos los vuelos."""
    return vuelo_service.listar_vuelos(db)

# === GET /vuelos/disponibles ===
@router.get("/disponibles", response_model=list[VueloRead])
def vuelos_disponibles(db: Session = Depends(get_db)):
    """Listar vuelos con asientos disponibles."""
    return vuelo_service.vuelos_disponibles(db)

# === GET /vuelos/{id} ===
@router.get("/{id}", response_model=VueloRead)
def obtener_vuelo(id: int, db: Session = Depends(get_db)):
    """Obtener detalles de un vuelo específico."""
    return vuelo_service.obtener_vuelo(db, id)

# === POST /vuelos/ ===
@router.post("/", response_model=VueloRead, status_code=status.HTTP_201_CREATED)
def crear_vuelo(
    datos: VueloCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # Solo admin
):
    """Crear un nuevo vuelo (solo administradores)."""
    return vuelo_service.crear_vuelo(db, datos)

# === PUT /vuelos/{id} ===
@router.put("/{id}", response_model=VueloRead)
def actualizar_vuelo(
    id: int,
    datos: VueloUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # Solo admin
):
    """Actualizar información de un vuelo (solo administradores)."""
    return vuelo_service.actualizar_vuelo(db, id, datos)

# === DELETE /vuelos/{id} ===
@router.delete("/{id}")
def eliminar_vuelo(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # Solo admin
):
    """Eliminar un vuelo (solo administradores)."""
    return vuelo_service.eliminar_vuelo(db, id)
