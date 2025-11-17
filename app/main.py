from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.openapi.utils import get_openapi
from app.db.database import Base, engine
from app.routes import auth_routes, usuario_routes, vuelo_routes, reserva_routes

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Instrumentator().instrument(app).expose(app)
    yield

app = FastAPI(
    title="FlyBlue API",
    version="1.0.0",
    lifespan=lifespan       
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FlyBlue API",
        version="1.0.0",
        description="Documentación de la API para FlyBlue",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth_routes.router)
app.include_router(usuario_routes.router)
app.include_router(vuelo_routes.router)
app.include_router(reserva_routes.router)

@app.get("/")
def root():
    return {"message": "🚀 FlyBlue backend running inside Docker!"}
