from typing import Optional, Dict
from app.schemas import Product, ProductIn


class ProductsService:
    def __init__(self):
        self._db: Dict[int, Product] = {}
        self._seq = 0

    def list(self) -> list[Product]:
        return list(self._db.values())

    def get(self, product_id: int) -> Optional[Product]:
        return self._db.get(product_id)

    def create(self, product_in: ProductIn) -> Product:
        self._seq += 1
        product = Product(id=self._seq, version=1, **product_in.model_dump())
        self._db[self._seq] = product
        return product

    def update(
        self, product_id: int, data: ProductIn, expected_version: Optional[int]
    ) -> Optional[Product]:
        cur = self._db.get(product_id)
        if not cur:
            return None

        if expected_version is not None and expected_version != cur.version:
            raise ValueError("version_mismatch")
        updated = Product(id=product_id, version=cur.version + 1, **data.model_dump())
        self._db[product_id] = updated
        return updated

    def delete(self, product_id: int) -> bool:
        return self._db.pop(product_id, None) is not None
