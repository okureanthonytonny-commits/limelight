from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Numeric


class ProductBase(SQLModel):
    """Shared properties for products."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0, sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None, max_length=255)


class Product(ProductBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    """Model for creating a product."""


class ProductRead(ProductBase):
    """Model for returning a product."""

    id: int
    created_at: datetime
    updated_at: datetime


class ProductUpdate(SQLModel):
    """Model for updating a product (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0, sa_column=Column(Numeric(10, 2), nullable=True))
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
