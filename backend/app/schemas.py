from datetime import datetime

from pydantic import BaseModel, Field


MAX_QUANTITY = 9_223_372_036_854_775_807
MAX_DESCRIPTION_LENGTH = 2000


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
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)
    quantity: int = Field(default=0, ge=0, le=MAX_QUANTITY)
    location: str = Field(default="A-01", max_length=64)
    min_stock: int = Field(default=5, ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)
    quantity: int | None = Field(default=None, ge=0, le=MAX_QUANTITY)
    location: str | None = Field(default=None, max_length=64)
    min_stock: int | None = Field(default=None, ge=0)


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
    delta: int = Field(ge=-MAX_QUANTITY, le=MAX_QUANTITY, description="Positive to add, negative to remove")
