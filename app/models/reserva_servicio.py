from sqlalchemy import Column, BigInteger, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

class ReservaServicio(Base):
    __tablename__ = "reserva_servicio"

    id = Column(BigInteger, primary_key=True, index=True)
    reserva_id = Column(BigInteger, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    servicio_id = Column(BigInteger, ForeignKey("servicios.id", ondelete="CASCADE"), nullable=False)

    cantidad = Column(BigInteger, default=1)
    subtotal = Column(Numeric(10, 2))

    # Relaciones
    reserva = relationship("Reserva", back_populates="servicios_reserva")
    servicio = relationship("Servicio")
