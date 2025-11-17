from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # id = número de identificación del usuario (no autoincremental)
    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(20), default="cliente", nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")