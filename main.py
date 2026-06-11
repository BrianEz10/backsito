from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.core.database import engine
from app.modules.health.router import router as health_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_roles(session)
        seed_unidades_medida(session)
        seed_admin_test(session)
        seed_estados_pedido(session)
        seed_formas_pago(session)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(categorias_router)
app.include_router(ingredientes_router)
app.include_router(productos_router)
app.include_router(direcciones_router)
app.include_router(pedidos_router)
app.include_router(admin_router)
app.include_router(catalogos_router)