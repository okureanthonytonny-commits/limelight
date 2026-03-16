from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Shared properties for users."""

    username: str = Field(..., max_length=50, unique=True)
    password_hash: str = Field(..., max_length=255)


class User(UserBase, table=True):
    """Database table model."""

    id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    """Model for creating a user."""


class UserRead(UserBase):
    """Model for returning a user."""

    id: int


class UserUpdate(SQLModel):
    """Model for updating a user (all fields optional)."""

    username: Optional[str] = None
    password_hash: Optional[str] = None