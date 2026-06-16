from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.core.config import settings
from app.core.database import engine
from app.modules.auth.router import router as auth_router
from app.modules.categorias.router import router as categorias_router
from app.modules.ingredientes.router import router as ingredientes_router
from app.modules.productos.router import router as productos_router
from app.core.database import Session
from app.db.seed import seed_admin_test, seed_estados_pedido, seed_formas_pago, seed_roles, seed_unidades_medida
from app.modules.direcciones.router import router as direcciones_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.admin.router import router as admin_router
from app.core.catalog_endpoints import router as catalogos_router
from app.modules.pagos.router import router as pagos_router
from app.modules.uploads.router import router as uploads_router
from app.modules.usuarios.router import router as usuarios_router
from app.core.rate_limit.rate_limit_middleware import RateLimitMiddleware
from app.core.logging_config import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.core.timing_middleware import TimingMiddleware

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_roles(session)
        seed_unidades_medida(session)
        seed_admin_test(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
        import cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
    yield


app = FastAPI(lifespan=lifespan)


register_exception_handlers(app)


app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/")
def root():
    return {"status": "ok", "app": "Food Store API", "docs": "/docs"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(categorias_router, prefix="/api/v1")
app.include_router(ingredientes_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")
app.include_router(direcciones_router, prefix="/api/v1")
app.include_router(pedidos_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(catalogos_router, prefix="/api/v1")
app.include_router(pagos_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
app.include_router(usuarios_router, prefix="/api/v1")