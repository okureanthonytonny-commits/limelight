from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class CartItemBase(SQLModel):
    """Shared properties for cart items."""

    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1, ge=1)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class CartItem(CartItemBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships – using string forward references
    user: Optional["User"] = Relationship(back_populates="cart_items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")


class CartItemCreate(SQLModel):
    """Model for creating a cart item."""

    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemRead(CartItemBase):
    """Model for returning a cart item."""

    id: int
    product: Optional["Product"] = None  # Include product details in response


class CartItemUpdate(SQLModel):
    """Model for updating a cart item."""

    quantity: Optional[int] = Field(default=None, ge=0)  # Allow 0 to remove