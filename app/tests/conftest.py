import pytest
from app.services import ProductsService
from app.schemas import ProductIn


@pytest.fixture
def service():
    return ProductsService()


@pytest.fixture
def populated_service(service):
    service.create(ProductIn(name="Banana", price=10.0))
    service.create(ProductIn(name="Maçã", price=5.0))
    return service
