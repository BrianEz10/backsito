from sqlmodel import SQLModel

class UserCreate(SQLModel):
    email: str
    nombre: str
    apellido: str
    celular: str | None = None
    password: str

class UserPublic(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None = None

class UserMeOut(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None
    roles: list[str]