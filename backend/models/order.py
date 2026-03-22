from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Numeric


# ============================================================
# OrderItem Model: Line items in an order
# ============================================================

class OrderItemBase(SQLModel):
    """Shared properties for order items."""

    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0, sa_column=Column(Numeric(10, 2), nullable=False))


class OrderItem(OrderItemBase, table=True):
    """Database table model for order items (product snapshots)."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="order_items")


class OrderItemRead(OrderItemBase):
    """Model for returning an order item."""

    id: int
    product: Optional["Product"] = None


# ============================================================
# Order Model: Main order containing multiple items
# ============================================================

class OrderBase(SQLModel):
    """Shared properties for orders."""

    user_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending", max_length=20)


class Order(OrderBase, table=True):
    """Database table model for orders."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderCreate(SQLModel):
    """Schema for creating an order (client just sends nothing, we use cart)."""

    pass  # No fields needed; server uses the user's cart


class OrderRead(OrderBase):
    """Model for returning an order with items."""

    id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []


class OrderStatusUpdate(SQLModel):
    """Model for updating order status."""

    status: str = Field(..., max_length=20)