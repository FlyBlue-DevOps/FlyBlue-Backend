"""
Módulo de seguridad para gestión de contraseñas y generación/validación de JWT en la aplicación FlyBlue.

Funciones principales:
- Hash y verificación de contraseñas con bcrypt.
- Creación y decodificación de tokens JWT para autenticación y autorización.
"""

from datetime import datetime, timedelta
from typing import Optional
import os

from passlib.context import CryptContext
from jose import jwt

# Cargar variables de entorno (ya usas python-dotenv en database.py)
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_in_production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano corresponde con el hash almacenado.

    Parametros:
        plain_password (str): Contraseña introducida por el usuario.
        hashed_password (str): Hash almacenado en base de datos.

    Retorna:
        bool: True si la contraseña es válida, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashea una contraseña para almacenamiento seguro usando bcrypt.

    Parametros:
        password (str): Contraseña en texto plano.

    Retorna:
        str: Hash seguro resultante.
    """
    return pwd_context.hash(password)

def create_access_token(subject: str, data: dict = None, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea y firma un token JWT para autenticación de usuario.

    Parametros:
        subject (str): Identificador principal del usuario (por ejemplo, email o id).
        data (dict, opcional): Claims adicionales (ejemplo: rol, id).
        expires_delta (timedelta, opcional): Tiempo personalizado de expiración.

    Retorna:
        str: Token JWT firmado y listo para transmisión al cliente.
    """
    to_encode = {"sub": subject}
    if data:
        to_encode.update(data)
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> dict:
    """
    Decodifica y verifica un token JWT usando la clave secreta.

    Parametros:
        token (str): Token JWT recibido del cliente.

    Retorna:
        dict: Payload decodificado con datos del usuario y claims.

    Lanza:
        jose.JWTError: Si el token es inválido o está expirado.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
