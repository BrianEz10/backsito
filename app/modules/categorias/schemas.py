from sqlmodel import SQLModel, Field

class CategoriaCreate(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: str | None = None
    imagen_url: str | None = None
    parent_id: int | None = None

class CategoriaUpdate(SQLModel):
    nombre:str | None = Field(default=None, max_length=100)
    descripcion: str | None = None
    imagen_url: str | None = None
    parent_id: int | None = None

class CategoriaOut(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    imagen_url: str | None
    parent_id: int | None

class CategoriaWithHijos(CategoriaOut):
    hijos: list["CategoriaWithHijos"] = []