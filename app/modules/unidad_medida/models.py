from sqlmodel import Field
from app.core.base import Base


class UnidadMedida(Base, table=True):
    __tablename__: str = "unidad_medida"

    nombre: str = Field(unique=True, nullable=False, max_length=50)
    simbolo: str = Field(unique=True, nullable=False, max_length=10)
    tipo: str = Field(nullable=False, max_length=20)