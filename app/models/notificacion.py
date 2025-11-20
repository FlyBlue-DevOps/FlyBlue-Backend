from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)

    titulo = Column(String(50), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(50), default="info")
    leido = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="notificaciones")
