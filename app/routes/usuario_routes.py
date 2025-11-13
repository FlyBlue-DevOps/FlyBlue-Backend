from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dto.usuario_dto import UsuarioRead, UsuarioBase
from app.models.usuario import Usuario
from app.core.auth import get_current_user, require_admin
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# === GET /usuarios/ ===
@router.get("/", response_model=list[UsuarioRead])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # solo admin
):
    """
    Listar todos los usuarios (solo para administradores)
    """
    return usuario_service.listar_usuarios(db)


# === GET /usuarios/{id} ===
@router.get("/{id}", response_model=UsuarioRead)
def obtener_usuario(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener la información de un usuario específico.
    Solo el propio usuario o un administrador puede consultar.
    """
    usuario = usuario_service.obtener_usuario_por_id(db, id)

    if current_user.rol != "admin" and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )

    return usuario


# === PUT /usuarios/{id} ===
@router.put("/{id}", response_model=UsuarioRead)
def actualizar_usuario(
    id: int,
    datos: UsuarioBase,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar los datos de un usuario.
    Un usuario solo puede actualizar su propia información.
    Los administradores pueden modificar cualquier usuario (incluido su rol).
    """
    return usuario_service.actualizar_usuario(db, id, datos, current_user)


# === DELETE /usuarios/{id} ===
@router.delete("/{id}")
def eliminar_usuario(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # solo admin
):
    """
    Eliminar un usuario del sistema (solo administradores)
    """
    return usuario_service.eliminar_usuario(db, id)