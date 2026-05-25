from sqlmodel import SQLModel, Field

class IngredienteCreate(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: str | None = None
    es_alergeno: bool = False

class IngredienteUpdate(SQLModel):
    nombre: str | None = Field(default=None, max_length=100)
    descripcion: str | None = None
    es_alergeno: bool | None = None

class IngredienteOut(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    es_alergeno: bool