from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories import usuario_repo
from app.dto.usuario_dto import UsuarioCreate, UsuarioBase
from app.models.usuario import Usuario

# === Crear usuario (registro manual o administrativo) ===
def registrar_usuario(db: Session, usuario: UsuarioCreate):
    existente = usuario_repo.obtener_usuario_por_email(db, usuario.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado."
        )
    return usuario_repo.crear_usuario(db, usuario)

# === Listar todos los usuarios (solo admin) ===
def listar_usuarios(db: Session):
    return usuario_repo.listar_usuarios(db)

# === Obtener un usuario por ID ===
def obtener_usuario_por_id(db: Session, id: int):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return usuario

# === Actualizar usuario ===
def actualizar_usuario(db: Session, id: int, datos: UsuarioBase, current_user: Usuario):
    usuario = obtener_usuario_por_id(db, id)

    # Permitir solo al admin o al propio usuario
    if current_user.rol != "admin" and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario."
        )

    usuario.nombre = datos.nombre
    usuario.email = datos.email

    # Solo el admin puede cambiar el rol
    if current_user.rol == "admin":
        usuario.rol = datos.rol

    db.commit()
    db.refresh(usuario)
    return usuario

# === Eliminar usuario ===
def eliminar_usuario(db: Session, id: int):
    usuario = obtener_usuario_por_id(db, id)
    db.delete(usuario)
    db.commit()
    return {"message": f"Usuario con id {id} eliminado correctamente."}
