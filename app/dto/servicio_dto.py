from pydantic import BaseModel
from typing import Optional

class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None

class ServicioRead(ServicioBase):
    id: int

    class Config:
        from_attributes = True
