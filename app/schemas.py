from pydantic import BaseModel, PositiveFloat
from typing import Optional


class ProductIn(BaseModel):
    name: str
    price: PositiveFloat
    description: Optional[str] = None


class Product(ProductIn):
    id: int
    version: int


class ListProductsResponse(BaseModel):
    data: list[Product]
    count: int


class CreateProductResponse(Product):
    pass
