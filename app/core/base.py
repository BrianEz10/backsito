from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, DateTime

class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    deleted_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))