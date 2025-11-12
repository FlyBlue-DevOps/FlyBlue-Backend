# app/services/auth_service.py
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.usuario_repo import obtener_usuario_por_email, crear_usuario
from app.dto.auth_dto import RegisterRequest, LoginRequest
from app.core.security import verify_password, create_access_token, get_password_hash

def register_user(db: Session, payload: RegisterRequest):
    # verifica si email o id ya existen
    existing_email = obtener_usuario_por_email(db, payload.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correo ya registrado")
    # Nota: si quieres, también comprueba ID duplicado con repo (añadir función)
    # usamos el repo crear_usuario (que espera DTO UsuarioCreate en tu repo)
    user_data = payload  # reutilizaremos el DTO ya definido en tu proyecto
    # hashed done in repository; if not, hash here, or you can call repository expecting clear password.
    return crear_usuario(db, user_data)

def authenticate_user(db: Session, login: LoginRequest):
    user = obtener_usuario_por_email(db, login.email)
    if not user:
        return None
    if not verify_password(login.contrasena, user.contrasena):
        return None
    return user

def create_token_for_user(user, expires_minutes: int = None):
    # subject puede ser el email; además incluir id y rol
    extra = {"id": user.id, "rol": user.rol}
    if expires_minutes:
        token = create_access_token(subject=str(user.email), data=extra, expires_delta=timedelta(minutes=expires_minutes))
    else:
        token = create_access_token(subject=str(user.email), data=extra)
    return token
