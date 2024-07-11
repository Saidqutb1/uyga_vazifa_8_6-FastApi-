from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode: True

class OrderBase(BaseModel):
    product_id: int
    quantity: int
    total_price: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    product: Product

    class Config:
        orm_mode: True
