from pydantic import BaseModel
from pydantic import Field
from datetime import datetime
from app.dto.reserva_servicio_dto import ReservaServicioRead

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
    asiento: str
    total: float
    servicios: list[ReservaServicioRead] = Field(default_factory=list, alias="servicios_reserva")

    class Config:
        orm_mode = True
