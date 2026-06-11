from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True, nullable=False)
    monto: float = Field(default=0, ge=0, decimal_places=2, max_digits=10)
    estado: str = Field(max_length=20)


    mp_preference_id: Optional[str] = Field(default=None, max_length=255)
    mp_init_point: Optional[str] = Field(default=None, max_length=500)
    mp_merchant_order_id: Optional[int] = Field(default=None, sa_type=BigInteger)


    mp_payment_id: Optional[int] = Field(default=None, sa_type=BigInteger, unique=True)
    mp_status: Optional[str] = Field(default=None, max_length=30)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)
    external_reference: str = Field(max_length=100, unique=True)
    idempotency_key: str = Field(nullable=False, max_length=100, unique=True)
    transaction_amount: Decimal = Field(default=0, ge=0, decimal_places=2, max_digits=10)
    payment_method_id: Optional[str] = Field(default=None, max_length=50)
    

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)