# app/dto/auth_dto.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None
    id: Optional[int] = None
    rol: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    contrasena: str

class RegisterRequest(BaseModel):
    id: int                 # tu ID nacional (no autoincremental)
    nombre: str
    email: EmailStr
    contrasena: str
    rol: Optional[str] = "cliente"
