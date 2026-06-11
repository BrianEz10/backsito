from sqlmodel import SQLModel, Field
from datetime import datetime

class AdminUserOut(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None = None
    roles: list[str] = []
    created_at: datetime
    deleted_at: datetime | None = None

class AdminUserUpdate(SQLModel):
    nombre: str | None = None
    apellido: str | None = None
    celular: str | None = None

class AdminAsignarRolesRequest(SQLModel):
    roles: list[str]

# Admin reusa entidades de auth/roles; falta AdminUnitOfWork.

class EstadoCount(SQLModel):
    estado: str
    cantidad: int

class ProductoVendido(SQLModel):
    nombre: str
    total_vendido: int

class PedidoReciente(SQLModel):
    id: int
    usuario_email: str
    total: float
    estado_codigo: str
    created_at: datetime

class DashboardResponse(SQLModel):
    total_pedidos: int
    ingresos_totales: float
    pedidos_por_estado: list[EstadoCount]
    productos_mas_vendidos: list[ProductoVendido]
    pedidos_recientes: list[PedidoReciente]