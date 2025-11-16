from pydantic import BaseModel

class ReservaServicioCreate(BaseModel):
    servicio_id: int
    cantidad: int = 1

class ReservaServicioRead(BaseModel):
    id: int
    servicio_id: int
    cantidad: int
    subtotal: float

    class Config:
        from_attributes = True
