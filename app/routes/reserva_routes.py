from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user, require_admin
from app.services import reserva_service
from app.dto.reserva_dto import ReservaCreate, ReservaUpdate, ReservaRead
from app.dto.servicio_dto import ServicioRead
from app.dto.reserva_servicio_dto import ReservaServicioRead
from app.models.usuario import Usuario

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# === GET /reservas/ ===
@router.get("/", response_model=list[ReservaRead])
def listar_reservas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol == "admin":
        return reserva_service.listar_reservas(db)
    return reserva_service.listar_reservas(db, current_user.id)

# === GET /reservas/{id} ===
@router.get("/{id}", response_model=ReservaRead)
def obtener_reserva(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.obtener_reserva(db, id, current_user)

# === POST /reservas/ ===
@router.post("/", response_model=ReservaRead, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    datos: ReservaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.crear_reserva(db, datos, current_user.id)

# === PUT /reservas/{id} ===
@router.put("/{id}", response_model=ReservaRead)
def actualizar_reserva(
    id: int,
    datos: ReservaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.actualizar_reserva(db, id, datos, current_user)

@router.post("/{id}/agregar-servicio", response_model=ReservaServicioRead)
def agregar_servicio_a_reserva(
    id: int,
    servicio_id: int,
    cantidad: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.agregar_servicio_a_reserva(db, id, servicio_id, cantidad, current_user)

@router.get("/{id}/servicios", response_model=list[ReservaServicioRead])
def obtener_servicios_de_reserva(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.obtener_servicios_de_reserva(db, id, current_user)

@router.delete("/{id}/eliminar-servicio")
def eliminar_servicio_de_reserva(
    id: int,
    servicio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return reserva_service.eliminar_servicio_de_reserva(db, id, servicio_id, current_user)

# === POST /reservas/{id}/confirmar ===
@router.post("/{id}/confirmar", response_model=ReservaRead)
def confirmar_reserva(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return reserva_service.confirmar_reserva(db, id)

# === DELETE /reservas/{id} ===
@router.delete("/{id}")
def eliminar_reserva(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    return reserva_service.eliminar_reserva(db, id)
