from sqlmodel import SQLModel
from datetime import datetime


class UsuarioOut(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None = None
    roles: list[str] = []
    created_at: datetime
    deleted_at: datetime | None = None


class UsuarioUpdate(SQLModel):
    nombre: str | None = None
    apellido: str | None = None
    celular: str | None = None


class AsignarRolesRequest(SQLModel):
    roles: list[str]


class PaginatedUsuarios(SQLModel):
    items: list[UsuarioOut]
    total: int
    page: int
    size: int
    pages: int