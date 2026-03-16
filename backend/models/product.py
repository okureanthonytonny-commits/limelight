from typing import Optional

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """Shared properties for products."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0, sa_column_kwargs={"type_": "NUMERIC(10,2)"})
    image_url: Optional[str] = Field(None, max_length=255)


class Product(ProductBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    """Model for creating a product."""


class ProductRead(ProductBase):
    """Model for returning a product."""

    id: int


class ProductUpdate(SQLModel):
    """Model for updating a product (all fields optional)."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0, sa_column_kwargs={"type_": "NUMERIC(10,2)"})
    image_url: Optional[str] = None
