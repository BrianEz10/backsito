from sqlmodel import SQLModel

class DireccionCreate(SQLModel):
    alias: str | None = None
    linea1: str
    linea2: str | None = None
    ciudad: str
    provincia: str | None = None
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool = False

class DireccionUpdate(SQLModel):
    alias: str | None = None
    linea1: str | None = None
    linea2: str | None = None
    ciudad: str | None = None
    provincia: str | None = None
    codigo_postal: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    es_principal: bool | None = None

class DireccionOut(SQLModel):
    id: int
    alias: str  | None 
    linea1: str
    linea2: str  | None 
    ciudad: str
    provincia: str  | None 
    codigo_postal: str  | None 
    latitud: float | None 
    longitud: float | None 
    es_principal: bool