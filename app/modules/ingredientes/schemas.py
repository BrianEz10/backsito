from sqlmodel import SQLModel, Field

class IngredienteCreate(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: str | None = None
    es_alergeno: bool = False
    stock_cantidad: int = Field(default=0, ge=0)

class IngredienteUpdate(SQLModel):
    nombre: str | None = Field(default=None, max_length=100)
    descripcion: str | None = None
    es_alergeno: bool | None = None
    stock_cantidad: int | None = Field(default=None, ge=0)

class IngredienteOut(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    es_alergeno: bool
    stock_cantidad: int