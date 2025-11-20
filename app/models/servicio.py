from sqlalchemy import Column, BigInteger, String, Text, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    
    reservas = relationship("ReservaServicio", back_populates="servicio")
