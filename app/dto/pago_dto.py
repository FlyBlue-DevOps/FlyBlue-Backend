from pydantic import BaseModel
from datetime import datetime

class PagoCreate(BaseModel):
    reserva_id: int
    metodo: str = "tarjeta"
    monto: float

class PagoRead(BaseModel):
    id: int
    reserva_id: int
    metodo: str
    monto: float
    moneda: str
    fecha: datetime
    estado: str

    class Config:
        from_attributes = True
