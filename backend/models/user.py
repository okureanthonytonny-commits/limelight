from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel



class UserBase(SQLModel):
    """Shared properties for users."""

    username: str = Field(..., max_length=50, unique=True)
    password_hash: str = Field(..., max_length=255)
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    role: str = Field(default="customer", max_length=50)


class User(UserBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships to cart and orders
    cart_items: List["CartItem"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Model for creating a user."""


class UserRead(UserBase):
    """Model for returning a user."""

    id: int


class UserUpdate(SQLModel):
    """Model for updating a user (all fields optional)."""

    username: Optional[str] = None
    password_hash: Optional[str] = None