from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class ItemPedidoRequest(SQLModel):
    producto_id: int
    cantidad: int = Field(ge=1)
    personalizacion: list[int] | None = None

class PedidoCreate(SQLModel):
    direccion_id: int | None = None
    forma_pago_codigo: str
    notas: str | None = None
    items: list[ItemPedidoRequest]

class DetallePedidoOut(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: float
    subtotal_snap: float
    personalizacion: list[int] | None = None
    created_at: datetime

class HistorialOut(SQLModel):
    pedido_id: int
    estado_desde: str | None = None
    estado_hacia: str
    usuario_id: int | None = None
    motivo: str | None = None
    created_at: datetime

class PedidoOut(SQLModel):
    id: int
    usuario_id: int
    direccion_id: int | None = None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: float
    descuento: float
    costo_envio: float
    total: float
    notas: str | None = None
    created_at: datetime
    detalles: list[DetallePedidoOut] = []
    historial: list[HistorialOut] = []
    
class AvanceEstadoRequest(SQLModel):
    estado_hacia: str
    motivo: str | None = None

class PaginatedPedidos(SQLModel):
    items: list[PedidoOut]
    total: int
    page: int
    size: int
    pages: int