from typing import Optional
from sqlmodel import SQLModel, Field

class FormaPagoCreate(SQLModel):
    codigo: str = Field(max_length=20)
    descripcion: str = Field(max_length=80)
    habilitado: bool = True

class FormaPagoUpdate(SQLModel):
    descripcion: Optional[str] = Field(default=None, max_length=80)
    habilitado: Optional[bool] = None

class FormaPagoOut(SQLModel):
    codigo: str
    descripcion: str
    habilitado: bool