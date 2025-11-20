from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

class ReservaServicio(Base):
    __tablename__ = "reserva_servicio"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id", ondelete="CASCADE"), nullable=False)

    cantidad = Column(Integer, default=1)
    subtotal = Column(Numeric(10, 2))

    # Relaciones
    reserva = relationship("Reserva", back_populates="servicios_reserva")
    servicio = relationship("Servicio")
