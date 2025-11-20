from sqlalchemy import Column, BigInteger, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    vuelo_id = Column(BigInteger, ForeignKey("vuelos.id"), nullable=False)
    fecha_reserva = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default="pendiente")
    clase = Column(String(20))
    asiento = Column(String(10))
    total = Column(Float, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="reservas")
    vuelo = relationship("Vuelo", back_populates="reservas")
    servicios_reserva = relationship("ReservaServicio", back_populates="reserva", cascade="all, delete-orphan")
    pago = relationship("Pago", back_populates="reserva", uselist=False)
