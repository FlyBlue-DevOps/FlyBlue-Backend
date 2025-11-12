from pydantic import BaseModel
from datetime import datetime

class ReservaBase(BaseModel):
    vuelo_id: int
    clase: str
    asiento: str | None = None
    total: float

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    estado: str | None = None
    clase: str | None = None
    asiento: str | None = None

class ReservaRead(BaseModel):
    id: int
    usuario_id: int
    vuelo_id: int
    fecha_reserva: datetime
    estado: str
    clase: str
    asiento: str | None
    total: float

    class Config:
        orm_mode = True
