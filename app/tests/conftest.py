import pytest
from app.services import ProductsService
from app.schemas import ProductIn
from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_products_service


@pytest.fixture
def service():
    svc = ProductsService()
    svc._db.clear()
    svc._seq = 0
    return svc


@pytest.fixture
def client(service: ProductsService):
    # faz o FastAPI usar ESSA instância de serviço
    app.dependency_overrides[get_products_service] = lambda: service

    with TestClient(app) as c:
        yield c

    # limpa overrides no final
    app.dependency_overrides.clear()


@pytest.fixture
def populated_service(service):
    service.create(ProductIn(name="Banana", price=10.0))
    service.create(ProductIn(name="Maçã", price=5.0))
    return service
