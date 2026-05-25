from sqlmodel import SQLModel, Field

class CategoriaEnProducto(SQLModel):
    categoria_id: int
    es_principal: bool = False

class IngredienteEnProducto(SQLModel):
    ingrediente_id: int
    cantidad: float = 0
    unidad_medida_id: int
    es_removible: bool = False

class ProductoCreate(SQLModel):
    nombre: str = Field(max_length=150)
    descripcion: str | None = None
    precio_base: float = Field(default=0, ge=0)
    imagenes_url: list[str] | None = None
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = True
    unidad_venta_id: int | None = None
    categorias: list[CategoriaEnProducto] = []
    ingredientes: list[IngredienteEnProducto] = []

class ProductoUpdate(SQLModel):
    nombre: str | None = Field(default=None, max_length=150)
    descripcion: str | None = None
    precio_base: float | None = Field(default=None, ge=0)
    imagenes_url: list[str] | None = None
    stock_cantidad: int | None = Field(default=None, ge=0)
    disponible: bool | None = None
    unidad_venta_id: int | None = None
    categorias: list[CategoriaEnProducto] | None = None
    ingredientes: list[IngredienteEnProducto] | None = None

class ProductoOut(SQLModel):
    id: int
    nombre: str
    descripcion: str | None = None
    precio_base: float = 0
    imagenes_url: list[str] | None = None
    stock_cantidad: int = 0
    disponible: bool = True
    unidad_venta_id: int | None = None

class DisponibilidadRequest(SQLModel):
    disponible: bool