from sqlmodel import Field, ForeignKey, Relationship, SQLModel, Column, Integer, ARRAY
from app.core.base import Base
from datetime import datetime, timezone


class Pedido(Base, table=True):
    __tablename__ = "pedidos"

    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    direccion_id: int | None = Field(default=None, foreign_key="direcciones_entrega.id")
    estado_codigo: str = Field(foreign_key="estados_pedido.codigo", nullable=False)
    forma_pago_codigo: str = Field(foreign_key="formas_pago.codigo", nullable=False)
    metodo_envio: str = Field(nullable=False, default="DOMICILIO")
    nombre_para: str | None = None
    subtotal: float = Field(nullable=False)
    descuento: float = Field(default=0.00, nullable=False)
    costo_envio: float = Field(default=50.00, nullable=False)
    total: float = Field(nullable=False, ge=1)
    notas: str | None = None

    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalles_pedido"

    pedido_id: int | None = Field(sa_column=Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), primary_key=True))
    producto_id: int | None = Field(sa_column=Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), primary_key=True))
    cantidad: int = Field(nullable=False, ge=1)
    nombre_snapshot: str = Field(max_length=200, nullable=False)
    precio_snapshot: float = Field(ge=0, nullable=False)
    subtotal_snap: float = Field(nullable=False)
    personalizacion: list[int] | None = Field(sa_column=Column(ARRAY(Integer)))
    created_at: datetime = Field(nullable=False, default_factory=lambda: datetime.now(timezone.utc))

    pedido: Pedido = Relationship(back_populates="detalles")


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estados_pedido"
    
    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(sa_column=Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE")))
    estado_desde: str | None = Field(foreign_key="estados_pedido.codigo", default=None)
    estado_hacia: str = Field(foreign_key="estados_pedido.codigo", nullable=False)
    usuario_id: int | None = Field(default=None, foreign_key="usuarios.id")
    motivo: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: Pedido = Relationship(back_populates="historial")