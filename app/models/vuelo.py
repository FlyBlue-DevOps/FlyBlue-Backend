from sqlalchemy import Column, BigInteger, String, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class Vuelo(Base):
    __tablename__ = "vuelos"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), nullable=False)
    salida = Column(DateTime, nullable=False)
    llegada = Column(DateTime, nullable=False)
    duracion = Column(Float, nullable=False)
    precio_base = Column(Float, nullable=False)
    asientos_disponibles = Column(BigInteger, nullable=False, default=100)
    
    reservas = relationship("Reserva", back_populates="vuelo", cascade="all, delete-orphan")
