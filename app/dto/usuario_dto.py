from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    id: int                      # ID personal (cedula/DNI)
    nombre: str
    email: EmailStr
    rol: Optional[str] = "cliente"

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioRead(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str
    fecha_registro: datetime

    class Config:
        orm_mode = True
