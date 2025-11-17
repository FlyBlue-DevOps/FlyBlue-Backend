from pydantic import BaseModel
from datetime import datetime

class NotificacionBase(BaseModel):
    titulo: str
    mensaje: str
    tipo: str = "info"

class NotificacionCreate(NotificacionBase):
    usuario_id: int

class NotificacionRead(NotificacionBase):
    id: int
    leido: bool
    fecha: datetime

    class Config:
        from_attributes = True
