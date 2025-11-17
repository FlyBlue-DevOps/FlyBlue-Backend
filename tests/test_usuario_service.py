# tests/test_usuario_service.py
"""
Pruebas unitarias para el servicio de usuarios (services/usuario_service.py).

Valida:
- Registro de usuarios
- Validación de emails duplicados
- Listado de usuarios
- Actualización de datos
- Control de permisos (admin vs usuario normal)
- Eliminación de usuarios
"""

import pytest
from fastapi import HTTPException

from app.services import usuario_service
from app.dto.usuario_dto import UsuarioCreate, UsuarioBase
from app.models.usuario import Usuario


# ========== PRUEBAS DE REGISTRO ==========

def test_registrar_usuario_exitoso(db_session):
    """
    Verifica que se pueda registrar un nuevo usuario correctamente.
    """
    datos = UsuarioCreate(
        id=11111111,
        nombre="Carlos López",
        email="carlos@test.com",
        contrasena="password123",
        rol="cliente"
    )
    
    usuario = usuario_service.registrar_usuario(db_session, datos)
    
    # Verificaciones
    assert usuario is not None
    assert usuario.id == 11111111
    assert usuario.nombre == "Carlos López"
    assert usuario.email == "carlos@test.com"
    assert usuario.rol == "cliente"
    assert usuario.contrasena != "password123"  # Debe estar hasheada
    assert len(usuario.contrasena) == 60  # Longitud de hash bcrypt


def test_registrar_usuario_email_duplicado(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que no se permita registrar dos usuarios con el mismo email.
    
    Debe lanzar HTTPException con código 400.
    """
    # Crear primer usuario
    create_usuario(usuario_cliente_data)
    
    # Intentar crear segundo usuario con mismo email
    datos_duplicados = UsuarioCreate(
        id=99999999,
        nombre="Otro Usuario",
        email=usuario_cliente_data["email"],  # Email duplicado
        contrasena="otra_password",
        rol="cliente"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.registrar_usuario(db_session, datos_duplicados)
    
    assert exc_info.value.status_code == 400
    assert "correo ya está registrado" in exc_info.value.detail.lower()


def test_registrar_usuario_admin(db_session):
    """
    Verifica que se pueda registrar un usuario con rol 'admin'.
    """
    datos = UsuarioCreate(
        id=88888888,
        nombre="Administrador",
        email="admin@flyblue.com",
        contrasena="admin_pass",
        rol="admin"
    )
    
    usuario = usuario_service.registrar_usuario(db_session, datos)
    
    assert usuario.rol == "admin"


# ========== PRUEBAS DE LISTADO ==========

def test_listar_usuarios_vacio(db_session):
    """
    Verifica que listar_usuarios() devuelva lista vacía cuando no hay usuarios.
    """
    usuarios = usuario_service.listar_usuarios(db_session)
    
    assert usuarios == []


def test_listar_usuarios_con_datos(db_session, create_usuario, usuario_cliente_data, usuario_admin_data):
    """
    Verifica que listar_usuarios() devuelva todos los usuarios registrados.
    """
    # Crear usuarios de prueba
    create_usuario(usuario_cliente_data)
    create_usuario(usuario_admin_data)
    
    usuarios = usuario_service.listar_usuarios(db_session)
    
    assert len(usuarios) == 2
    assert any(u.email == usuario_cliente_data["email"] for u in usuarios)
    assert any(u.email == usuario_admin_data["email"] for u in usuarios)


# ========== PRUEBAS DE OBTENCIÓN POR ID ==========

def test_obtener_usuario_por_id_existente(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que se pueda obtener un usuario por su ID.
    """
    usuario_creado = create_usuario(usuario_cliente_data)
    
    usuario = usuario_service.obtener_usuario_por_id(db_session, usuario_creado.id)
    
    assert usuario is not None
    assert usuario.id == usuario_cliente_data["id"]
    assert usuario.email == usuario_cliente_data["email"]


def test_obtener_usuario_por_id_inexistente(db_session):
    """
    Verifica que obtener_usuario_por_id() lance excepción cuando el ID no existe.
    
    Debe lanzar HTTPException con código 404.
    """
    id_inexistente = 99999999
    
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.obtener_usuario_por_id(db_session, id_inexistente)
    
    assert exc_info.value.status_code == 404
    assert "no encontrado" in exc_info.value.detail.lower()


# ========== PRUEBAS DE ACTUALIZACIÓN ==========

def test_actualizar_usuario_por_mismo_usuario(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que un usuario pueda actualizar sus propios datos.
    """
    usuario = create_usuario(usuario_cliente_data)
    
    # Usuario actualiza su propio perfil
    datos_actualizados = UsuarioBase(
        id=usuario.id,
        nombre="Nuevo Nombre",
        email="nuevo_email@test.com",
        rol="cliente"
    )
    
    usuario_actualizado = usuario_service.actualizar_usuario(
        db_session,
        usuario.id,
        datos_actualizados,
        current_user=usuario
    )
    
    assert usuario_actualizado.nombre == "Nuevo Nombre"
    assert usuario_actualizado.email == "nuevo_email@test.com"
    assert usuario_actualizado.rol == "cliente"  # Rol no cambia


def test_actualizar_usuario_rol_sin_permisos(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que un usuario normal NO pueda cambiar su propio rol.
    
    Solo admins pueden cambiar roles.
    """
    usuario = create_usuario(usuario_cliente_data)
    
    # Usuario intenta cambiar su rol a admin
    datos_actualizados = UsuarioBase(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        rol="admin"  # Intenta cambiar a admin
    )
    
    usuario_actualizado = usuario_service.actualizar_usuario(
        db_session,
        usuario.id,
        datos_actualizados,
        current_user=usuario
    )
    
    # El rol NO debe cambiar porque no es admin
    assert usuario_actualizado.rol == "cliente"


def test_actualizar_usuario_por_admin(db_session, create_usuario, usuario_cliente_data, usuario_admin_data):
    """
    Verifica que un admin pueda actualizar cualquier usuario, incluyendo el rol.
    """
    cliente = create_usuario(usuario_cliente_data)
    admin = create_usuario(usuario_admin_data)
    
    # Admin actualiza el cliente
    datos_actualizados = UsuarioBase(
        id=cliente.id,
        nombre="Nombre Cambiado Por Admin",
        email=cliente.email,
        rol="admin"  # Admin puede cambiar rol
    )
    
    usuario_actualizado = usuario_service.actualizar_usuario(
        db_session,
        cliente.id,
        datos_actualizados,
        current_user=admin
    )
    
    assert usuario_actualizado.nombre == "Nombre Cambiado Por Admin"
    assert usuario_actualizado.rol == "admin"  # El rol SÍ cambió


def test_actualizar_usuario_sin_permisos(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que un usuario NO pueda actualizar datos de otro usuario.
    
    Debe lanzar HTTPException con código 403.
    """
    usuario1_data = usuario_cliente_data.copy()
    usuario2_data = {
        "id": 22222222,
        "nombre": "Otro Usuario",
        "email": "otro@test.com",
        "contrasena": "pass123",
        "rol": "cliente"
    }
    
    usuario1 = create_usuario(usuario1_data)
    usuario2 = create_usuario(usuario2_data)
    
    # Usuario1 intenta actualizar a Usuario2
    datos_actualizados = UsuarioBase(
        id=usuario2.id,
        nombre="Intento de Modificación",
        email=usuario2.email,
        rol="cliente"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.actualizar_usuario(
            db_session,
            usuario2.id,
            datos_actualizados,
            current_user=usuario1
        )
    
    assert exc_info.value.status_code == 403
    assert "no tienes permisos" in exc_info.value.detail.lower()


# ========== PRUEBAS DE ELIMINACIÓN ==========

def test_eliminar_usuario_existente(db_session, create_usuario, usuario_cliente_data):
    """
    Verifica que se pueda eliminar un usuario correctamente.
    """
    usuario = create_usuario(usuario_cliente_data)
    
    resultado = usuario_service.eliminar_usuario(db_session, usuario.id)
    
    assert "eliminado correctamente" in resultado["message"].lower()
    
    # Verificar que ya no existe
    with pytest.raises(HTTPException):
        usuario_service.obtener_usuario_por_id(db_session, usuario.id)


def test_eliminar_usuario_inexistente(db_session):
    """
    Verifica que eliminar un usuario inexistente lance excepción.
    
    Debe lanzar HTTPException con código 404.
    """
    id_inexistente = 99999999
    
    with pytest.raises(HTTPException) as exc_info:
        usuario_service.eliminar_usuario(db_session, id_inexistente)
    
    assert exc_info.value.status_code == 404


def test_eliminar_usuario_con_reservas(db_session, create_usuario, create_vuelo, usuario_cliente_data, vuelo_data):
    """
    Verifica que al eliminar un usuario, se eliminen sus reservas (cascade).
    """
    from app.models.reserva import Reserva
    
    usuario = create_usuario(usuario_cliente_data)
    vuelo = create_vuelo(vuelo_data)
    
    # Crear reserva asociada al usuario
    reserva = Reserva(
        usuario_id=usuario.id,
        vuelo_id=vuelo.id,
        clase="económica",
        total=150000.0
    )
    db_session.add(reserva)
    db_session.commit()
    
    # Eliminar usuario
    usuario_service.eliminar_usuario(db_session, usuario.id)
    
    # Verificar que la reserva también se eliminó
    reservas = db_session.query(Reserva).filter(Reserva.usuario_id == usuario.id).all()
    assert len(reservas) == 0