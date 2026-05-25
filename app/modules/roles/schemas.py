from sqlmodel import SQLModel

class RolCreate(SQLModel):
    codigo: str
    nombre: str
    descripcion: str | None = None

class RolUpdate(SQLModel):
    nombre: str | None = None
    descripcion: str | None = None

class RolOut(SQLModel):
    codigo: str
    nombre: str
    descripcion: str | None = None