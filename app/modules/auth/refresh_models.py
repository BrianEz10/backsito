from sqlmodel import Field
from app.core.base import Base
from datetime import datetime

class RefreshToken(Base, table=True):
    __tablename__ = "refresh_tokens"

    usuario_id: int = Field(foreign_key="usuarios.id")
    token_hash: str = Field(unique=True)
    expires_at: datetime
    revoked_at: datetime | None = None