from typing import TYPE_CHECKING
from sqlmodel import Relationship, Field, SQLModel
from app.modules.roles.associations import UsuarioRol


if TYPE_CHECKING:
    from app.modules.usuarios.models import Usuario


class Rol(SQLModel, table=True):
    __tablename__: str = "roles"

    codigo: str = Field(primary_key=True, max_length=20)
    nombre: str = Field(unique=True, max_length=50)
    descripcion: str | None = None

    usuarios: list["Usuario"] = Relationship(
        back_populates="roles", link_model=UsuarioRol,
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.usuario_id, UsuarioRol.rol_codigo]"
        }
    )