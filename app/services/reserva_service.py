from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import reserva_repo, reserva_servicio_repo
from app.models.vuelo import Vuelo
from app.models.usuario import Usuario
from app.models.reserva_servicio import ReservaServicio
from app.dto.reserva_dto import ReservaCreate, ReservaUpdate


def listar_reservas(db: Session, usuario_id: int = None):
    """Lista reservas (todas si es admin o solo las del usuario autenticado)."""
    if usuario_id:
        return reserva_repo.listar_reservas(db, usuario_id)
    return reserva_repo.listar_reservas(db)


def obtener_reserva(db: Session, reserva_id: int, current_user: Usuario):
    """Obtiene una reserva validando permisos del usuario."""
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta reserva"
        )

    return reserva


def crear_reserva(db: Session, datos: ReservaCreate, usuario_id: int):
    """Crea una nueva reserva y reduce los asientos disponibles."""
    vuelo = db.query(Vuelo).filter(Vuelo.id == datos.vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    if vuelo.asientos_disponibles <= 0:
        raise HTTPException(status_code=400, detail="No hay asientos disponibles")

    nueva = reserva_repo.crear_reserva(db, datos, usuario_id)
    vuelo.asientos_disponibles -= 1
    db.commit()
    return nueva


def actualizar_reserva(db: Session, reserva_id: int, datos: ReservaUpdate, current_user: Usuario):
    """Permite modificar una reserva solo si pertenece al usuario o es admin."""
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta reserva")

    reserva = reserva_repo.actualizar_reserva(db, reserva_id, datos)
    return reserva


def confirmar_reserva(db: Session, reserva_id: int):
    """Confirma una reserva pendiente."""
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if reserva.estado == "confirmada":
        raise HTTPException(status_code=400, detail="La reserva ya está confirmada")

    reserva.estado = "confirmada"
    db.commit()
    db.refresh(reserva)
    return reserva


def eliminar_reserva(db: Session, reserva_id: int, current_user: Usuario):
    """Elimina una reserva y libera un asiento si corresponde."""
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if current_user.rol != "admin" and reserva.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta reserva")

    vuelo = reserva.vuelo
    if vuelo:
        vuelo.asientos_disponibles += 1

    db.delete(reserva)
    db.commit()

    return {"message": f"Reserva {reserva_id} eliminada correctamente"}

def agregar_servicio_a_reserva(db, reserva_id: int, servicio_id: int, cantidad: int, current_user):
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    agregado = reserva_servicio_repo.agregar_servicio(
        db, reserva_id, servicio_id, cantidad
    )

    if not agregado:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    return agregado

def obtener_servicios_de_reserva(db, reserva_id: int, current_user):
    reserva = reserva_repo.obtener_reserva(db, reserva_id)

    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    return reserva_servicio_repo.obtener_servicios_de_reserva(db, reserva_id)


def eliminar_servicio_de_reserva(db, reserva_id: int, servicio_id: int, current_user):
    reserva = reserva_repo.obtener_reserva(db, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.usuario_id != current_user.id and current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    servicio_en_reserva = db.query(ReservaServicio).filter(
        ReservaServicio.servicio_id == servicio_id
    ).first()

    if not servicio_en_reserva:
        raise HTTPException(status_code=404, detail="Servicio no encontrado en la reserva")

    db.delete(servicio_en_reserva)
    db.commit()

    return {"message": f"Servicio {servicio_id} eliminado de la reserva {reserva_id} correctamente"}
