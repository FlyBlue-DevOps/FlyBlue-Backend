from pydantic import BaseModel
from datetime import datetime

class VueloBase(BaseModel):
    id: int
    origen: str
    destino: str
    salida: datetime
    llegada: datetime
    duracion: float
    precio_base: float
    asientos_disponibles: int

class VueloCreate(VueloBase):
    pass

class VueloUpdate(VueloBase):
    pass

class VueloRead(VueloBase):
    pass

    class Config:
        orm_mode = True
