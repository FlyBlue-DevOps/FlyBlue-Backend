from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.routes import auth_routes
from app.routes import usuario_routes
from app.routes import vuelo_routes
from app.routes import reserva_routes
from app.routes import servicio_routes
from app.routes import pago_routes
from app.routes import notificacion_routes

# Prometheus
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge
import time

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlyBlue API", version="1.0.0")

# Endpoint de métricas para Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# === MÉTRICAS PERSONALIZADAS ===

# Contador del endpoint root (mantener el original)
root_counter = Counter('flyblue_root_requests_total', 'Total de requests al root')

# Contador de requests por endpoint, método HTTP y status code
request_counter = Counter(
    'flyblue_requests_total',
    'Total de HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Histograma para medir la duración de las requests
request_duration = Histogram(
    'flyblue_request_duration_seconds',
    'Duración de las HTTP requests en segundos',
    ['method', 'endpoint']
)

# Gauge para requests en progreso
requests_in_progress = Gauge(
    'flyblue_requests_in_progress',
    'Número de requests en progreso',
    ['method', 'endpoint']
)

# === MIDDLEWARE PARA CAPTURAR MÉTRICAS AUTOMÁTICAMENTE ===

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # Excluir el endpoint /metrics del monitoreo
    if request.url.path == "/metrics":
        return await call_next(request)
    
    # Incrementar gauge de requests en progreso
    requests_in_progress.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    # Medir tiempo de inicio
    start_time = time.time()
    
    try:
        # Procesar la request
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        # Calcular duración
        duration = time.time() - start_time
        
        # Decrementar gauge de requests en progreso
        requests_in_progress.labels(
            method=request.method,
            endpoint=request.url.path
        ).dec()
        
        # Registrar contador de requests
        request_counter.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=status_code
        ).inc()
        
        # Registrar duración
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
    
    return response


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
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
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


# Incluir rutas
app.include_router(auth_routes.router)
app.include_router(usuario_routes.router)
app.include_router(vuelo_routes.router)
app.include_router(reserva_routes.router)
app.include_router(servicio_routes.router)
app.include_router(pago_routes.router)
app.include_router(notificacion_routes.router)


@app.get("/")
def root():
    root_counter.inc()
    return {"message": "FlyBlue backend running inside Docker!"}
