from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field


if TYPE_CHECKING:
    from app.modules.productos.models import Producto
    from app.modules.ingredientes.models import Ingrediente


class ProductoCategoria(SQLModel, table=True):
    __tablename__: str = "producto_categoria"

    producto_id: int | None = Field(
        default=None, foreign_key="productos.id", primary_key=True
    )
    categoria_id: int | None = Field(
        default=None, foreign_key="categorias.id", primary_key=True
    )
    es_principal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductoIngrediente(SQLModel, table=True):
    __tablename__: str = "producto_ingrediente"

    producto_id: int | None = Field(default=None, foreign_key="productos.id", primary_key=True)
    ingrediente_id: int | None = Field(default=None, foreign_key="ingredientes.id", primary_key=True)
    cantidad: float = Field(default=0)
    unidad_medida_id: int = Field(default=None, foreign_key="unidad_medida.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    es_removible: bool = Field(default=False)
    producto: "Producto" = Relationship(back_populates="producto_ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="producto_ingredientes")