from sqlmodel import Field, Relationship
from app.core.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.usuarios.models import Usuario

class DireccionEntrega(Base, table=True):
    __tablename__: str = "direcciones_entrega"

    usuario_id: int = Field(foreign_key="usuarios.id")
    alias: str | None = None
    linea1: str
    linea2: str | None = None
    ciudad: str
    provincia: str | None = None
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool = Field(default=False)

    usuario: "Usuario" = Relationship(back_populates="direcciones")