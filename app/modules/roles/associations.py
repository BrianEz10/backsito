from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class UsuarioRol(SQLModel, table=True):
    __tablename__: str = "usuario_rol"

    usuario_id: int | None = Field(
        default=None, foreign_key="usuarios.id", primary_key=True
    )
    rol_codigo: str | None = Field(
        default=None, foreign_key="roles.codigo", primary_key=True
    )
    asignado_por_id: int | None = Field(default=None, foreign_key="usuarios.id")
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))