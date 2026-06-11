from sqlmodel import SQLModel, Field
from datetime import datetime

class AdminUserOut(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None = None
    roles: list[str] = []
    created_at: datetime
    deleted_at: datetime | None = None

class AdminUserUpdate(SQLModel):
    nombre: str | None = None
    apellido: str | None = None
    celular: str | None = None

class AdminAsignarRolesRequest(SQLModel):
    roles: list[str]

# Admin reusa entidades de auth/roles; falta AdminUnitOfWork.