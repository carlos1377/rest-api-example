from app.services import ProductsService


def get_products_service() -> ProductsService:
    return ProductsService()
