# app/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_user

from app.db.database import get_db
from app.dto.auth_dto import LoginRequest, RegisterRequest, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # registra y retorna token inmediatamente (opcional)
    user = auth_service.register_user(db, payload)
    if not user:
        raise HTTPException(status_code=400, detail="No se pudo crear el usuario")
    token = auth_service.create_token_for_user(user)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    token = auth_service.create_token_for_user(user)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "nombre": current_user.nombre, "rol": current_user.rol}
