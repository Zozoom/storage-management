from datetime import datetime

from pydantic import BaseModel, Field


MAX_STOCK = 2_147_483_647


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)
    quantity: int = Field(default=0, ge=0, le=MAX_STOCK)
    location: str = Field(default="A-01", max_length=64)
    min_stock: int = Field(default=5, ge=0, le=MAX_STOCK)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)
    quantity: int | None = Field(default=None, ge=0, le=MAX_STOCK)
    location: str | None = Field(default=None, max_length=64)
    min_stock: int | None = Field(default=None, ge=0, le=MAX_STOCK)


class ItemOut(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None
    quantity: int
    location: str
    min_stock: int
    updated_at: datetime
    low_stock: bool = False

    model_config = {"from_attributes": True}


class StockAdjust(BaseModel):
    delta: int = Field(
        description="Positive to add, negative to remove",
        ge=-MAX_STOCK,
        le=MAX_STOCK,
    )
