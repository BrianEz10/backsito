from sqlmodel import SQLModel
from datetime import datetime


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


class TotalPorFormaPago(SQLModel):
    forma_pago: str
    total: float


class DashboardResponse(SQLModel):
    total_pedidos: int
    ingresos_totales: float
    pedidos_por_estado: list[EstadoCount]
    productos_mas_vendidos: list[ProductoVendido]
    pedidos_recientes: list[PedidoReciente]
    total_por_forma_pago: list[TotalPorFormaPago] = []