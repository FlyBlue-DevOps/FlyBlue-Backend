from sqlalchemy import Column, BigInteger, ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(BigInteger, primary_key=True, index=True)
    reserva_id = Column(BigInteger, ForeignKey("reservas.id"), nullable=False)
    metodo = Column(String(50), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(10), default="USD")
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), default="completado")
    referencia = Column(String(100), nullable=True)

    reserva = relationship("Reserva", back_populates="pago")
