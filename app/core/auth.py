# app/core/auth.py
"""Módulo de utilidades de autenticación.

Contiene dependencias reutilizables para obtener el usuario actual desde
tokens OAuth2 y para verificar permisos de administrador.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Any

from app.db.database import get_db
from app.models.usuario import Usuario
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Dependencia de FastAPI que devuelve el usuario asociado al token.

    Parámetros:
    - token: token JWT extraído automáticamente del header Authorization
      usando el esquema Bearer (ineludible cuando se declara como Depends(oauth2_scheme)).
    - db: sesión de SQLAlchemy inyectada con Depends(get_db).

    Comportamiento:
    - Decodifica el token llamando a `decode_access_token` (que lanza
      excepciones de JWTError en caso de token inválido o expirado).
    - Espera encontrar en el payload los campos "sub" y "id".
    - Busca en la base de datos el usuario por `id` y lo retorna.

    Retorna:
    - Una instancia de `Usuario` cuando el token y el usuario son válidos.

    Excepciones:
    - Lanza `HTTPException(status_code=401)` si el token no se puede validar
      o faltan campos esperados en el payload.
    - Lanza `HTTPException(status_code=401)` si no existe el usuario en DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: Any = decode_access_token(token)
        # Se esperan 'sub' (subject) y 'id' en el payload del JWT
        sub = payload.get("sub")
        user_id = payload.get("id")
        if sub is None or user_id is None:
            raise credentials_exception
    except JWTError:
        # Cubre tokens inválidos o expirados
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        # Si no hay usuario asociado al id del token
        raise credentials_exception
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> bool:
    """Dependencia que exige que el `current_user` tenga rol de administrador.

    Parámetros:
    - current_user: usuario inyectado por la dependencia `get_current_user`.

    Comportamiento:
    - Comprueba el campo `rol` del usuario (ignorando mayúsculas/minúsculas).
    - Si el rol no es "admin", lanza `HTTPException` con código 403.

    Retorna:
    - True si el usuario tiene permisos de administrador.

    Excepciones:
    - `HTTPException(status_code=403)` cuando el usuario no es admin.
    """
    if (current_user.rol or "").lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requieren permisos de administrador")
    return True
