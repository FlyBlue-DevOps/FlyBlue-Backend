from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class Vuelo(Base):
    __tablename__ = "vuelos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), nullable=False)
    salida = Column(DateTime, nullable=False)
    llegada = Column(DateTime, nullable=False)
    duracion = Column(Float, nullable=False)
    precio_base = Column(Float, nullable=False)
    asientos_disponibles = Column(Integer, nullable=False, default=100)
    
    reservas = relationship("Reserva", back_populates="vuelo", cascade="all, delete-orphan")
