# tests/test_security.py
"""
Pruebas unitarias para el módulo de seguridad (core/security.py).

Valida:
- Hash de contraseñas con bcrypt
- Verificación de contraseñas
- Creación de tokens JWT
- Decodificación de tokens JWT
- Manejo de tokens expirados o inválidos
"""

import pytest
import warnings
from datetime import timedelta
from jose import JWTError

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)

# Ignorar el DeprecationWarning de datetime.utcnow()
# Este warning viene del código de producción que no podemos modificar
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


# ========== PRUEBAS DE HASHING ==========

def test_get_password_hash():
    """
    Verifica que get_password_hash() genere un hash válido de bcrypt.
    
    Un hash bcrypt:
    - Siempre empieza con "$2b$"
    - Tiene 60 caracteres
    - Incluye el salt automáticamente
    """
    password = "mi_contraseña_segura_123"
    hashed = get_password_hash(password)
    
    # Verificaciones
    assert hashed is not None
    assert isinstance(hashed, str)
    assert len(hashed) == 60  # Longitud estándar de bcrypt
    assert hashed.startswith("$2b$")  # Formato bcrypt
    assert hashed != password  # No debe ser texto plano


def test_verify_password_correcto():
    """
    Verifica que verify_password() valide correctamente una contraseña.
    """
    password = "password123"
    hashed = get_password_hash(password)
    
    # La contraseña correcta debe validarse
    assert verify_password(password, hashed) is True


def test_verify_password_incorrecto():
    """
    Verifica que verify_password() rechace contraseñas incorrectas.
    """
    password = "password123"
    hashed = get_password_hash(password)
    
    # Contraseñas incorrectas deben ser rechazadas
    assert verify_password("password_incorrecta", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password("PASSWORD123", hashed) is False  # Case-sensitive


def test_hash_diferente_cada_vez():
    """
    Verifica que el mismo password genere hashes diferentes (por el salt).
    
    Esto es importante para seguridad: dos usuarios con la misma contraseña
    no deben tener el mismo hash en la BD.
    """
    password = "misma_contraseña"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 != hash2  # Hashes diferentes
    assert verify_password(password, hash1) is True  # Ambos válidos
    assert verify_password(password, hash2) is True


# ========== PRUEBAS DE JWT ==========

def test_create_access_token():
    """
    Verifica que create_access_token() genere un JWT válido.
    """
    subject = "usuario@test.com"
    data = {"id": 12345, "rol": "cliente"}
    
    token = create_access_token(subject, data)
    
    # Verificaciones básicas
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50  # JWT típicamente tiene más de 100 caracteres
    assert token.count(".") == 2  # JWT tiene formato: header.payload.signature


def test_decode_access_token():
    """
    Verifica que decode_access_token() decodifique correctamente un JWT.
    """
    subject = "usuario@test.com"
    data = {"id": 99999, "rol": "admin"}
    
    token = create_access_token(subject, data)
    payload = decode_access_token(token)
    
    # Verificar que el payload contiene los datos correctos
    assert payload["sub"] == subject
    assert payload["id"] == 99999
    assert payload["rol"] == "admin"
    assert "exp" in payload  # Debe tener fecha de expiración
    assert "iat" in payload  # Debe tener fecha de emisión


def test_token_con_expiracion_custom():
    """
    Verifica que se pueda crear un token con tiempo de expiración personalizado.
    """
    subject = "test@test.com"
    expires_delta = timedelta(minutes=5)
    
    token = create_access_token(subject, expires_delta=expires_delta)
    payload = decode_access_token(token)
    
    assert payload["sub"] == subject
    assert "exp" in payload


def test_decode_token_invalido():
    """
    Verifica que decode_access_token() lance excepción con token inválido.
    """
    token_invalido = "esto.no.es.un.token.valido"
    
    with pytest.raises(JWTError):
        decode_access_token(token_invalido)


def test_decode_token_corrupto():
    """
    Verifica que se rechacen tokens modificados (sin firma válida).
    """
    subject = "usuario@test.com"
    token = create_access_token(subject)
    
    # Modificar el token (corromper la firma)
    token_corrupto = token[:-10] + "XXXXXXXXXX"
    
    with pytest.raises(JWTError):
        decode_access_token(token_corrupto)


def test_token_sin_datos_adicionales():
    """
    Verifica que se pueda crear un token solo con subject (sin data).
    """
    subject = "simple@test.com"
    token = create_access_token(subject)
    payload = decode_access_token(token)
    
    assert payload["sub"] == subject
    assert "exp" in payload
    assert "iat" in payload


# ========== PRUEBAS DE INTEGRACIÓN ==========

def test_flujo_completo_hash_y_verificacion():
    """
    Prueba el flujo completo: hash, almacenamiento simulado y verificación.
    
    Simula lo que pasa en un registro y login real.
    """
    # 1. Usuario se registra
    password_original = "ContraseñaSegura123!"
    hashed_for_db = get_password_hash(password_original)
    
    # 2. Usuario intenta login con contraseña correcta
    login_exitoso = verify_password(password_original, hashed_for_db)
    assert login_exitoso is True
    
    # 3. Usuario intenta login con contraseña incorrecta
    login_fallido = verify_password("ContraseñaIncorrecta", hashed_for_db)
    assert login_fallido is False


def test_flujo_completo_jwt():
    """
    Prueba el flujo completo de JWT: crear, decodificar y usar datos.
    
    Simula lo que pasa en login y acceso a endpoints protegidos.
    """
    # 1. Usuario hace login exitoso
    user_email = "juan@flyblue.com"
    user_id = 12345678
    user_rol = "cliente"
    
    token = create_access_token(
        subject=user_email,
        data={"id": user_id, "rol": user_rol}
    )
    
    # 2. Usuario accede a endpoint protegido
    payload = decode_access_token(token)
    
    # 3. Verificar que se puede extraer la info del usuario
    assert payload["sub"] == user_email
    assert payload["id"] == user_id
    assert payload["rol"] == user_rol