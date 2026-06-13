from sqlmodel import Field, SQLModel


class EstadoPedido(SQLModel, table=True):
    __tablename__: str = "estados_pedido"

    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(nullable=False, max_length=80)
    orden: int = Field(nullable=False)
    es_terminal: bool = Field(nullable=False, default=False)