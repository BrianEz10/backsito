from sqlmodel import Field, Relationship
from app.core.base import Base
from app.modules.roles.associations import UsuarioRol
from app.modules.roles.models import Rol
from app.modules.direcciones.models import DireccionEntrega


class Usuario(Base, table=True):
    __tablename__ = "usuarios"

    email: str = Field(unique=True)
    nombre: str
    apellido: str
    celular: str | None = None
    hashed_password: str

    roles: list["Rol"] = Relationship(
        back_populates="usuarios", link_model=UsuarioRol,
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.usuario_id, UsuarioRol.rol_codigo]"
        }
    )

    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")