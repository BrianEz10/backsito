from datetime import datetime
from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator

class RegisterRequest(SQLModel):
    nombre: str
    apellido: str
    email: EmailStr
    celular: str | None = None
    password: str

    @field_validator("nombre", "apellido")
    @classmethod
    def name_length(cls, v: str) -> str:
        if len(v) < 2 or len(v) > 80:
            raise ValueError("Debe tener entre 2 y 80 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class UserPublic(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None = None

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    celular: str | None
    roles: list[str]
    created_at: datetime

class LoginRequest(SQLModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v