from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.dto.usuario_dto import UsuarioCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def crear_usuario(db: Session, usuario: UsuarioCreate):
    hashed_password = get_password_hash(usuario.contrasena)
    nuevo_usuario = Usuario(
        id=usuario.id,  # se usa el número de identificación personal
        nombre=usuario.nombre,
        email=usuario.email,
        contrasena=hashed_password,
        rol=usuario.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

def obtener_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def listar_usuarios(db: Session):
    return db.query(Usuario).all()
