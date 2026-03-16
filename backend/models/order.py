from typing import Optional

from sqlmodel import Field, SQLModel


class OrderBase(SQLModel):
    """Shared properties for orders."""

    user_id: int
    product_id: int
    quantity: int = Field(..., gt=0)
    total_price: float = Field(..., gt=0, sa_column_kwargs={"type_": "NUMERIC(10,2)"})


class Order(OrderBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)


class OrderCreate(OrderBase):
    """Model for creating an order."""


class OrderRead(OrderBase):
    """Model for returning an order."""

    id: int


class OrderUpdate(SQLModel):
    """Model for updating an order (all fields optional)."""

    quantity: Optional[int] = None
    total_price: Optional[float] = Field(None, gt=0, sa_column_kwargs={"type_": "NUMERIC(10,2)"})