from sqlmodel import Field, SQLModel


class FormaPago(SQLModel, table=True):
    __tablename__: str = "formas_pago"

    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(nullable=False ,max_length=80)
    habilitado: bool = Field(default=True, nullable=False)