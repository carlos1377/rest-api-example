import pytest
from app.schemas import Product, ProductIn


def test_product_schema():
    product = Product(id=1, name="Test Product", price=9.99, version=1)
    assert product.id == 1
    assert product.name == "Test Product"
    assert product.price == 9.99
    assert product.version == 1
    assert product.description is None

    assert product.model_dump() == {
        "id": 1,
        "name": "Test Product",
        "price": 9.99,
        "version": 1,
        "description": None,
    }


def test_product_in_schema():
    product_in = ProductIn(name="Test Product", price=9.99, description="Foo Bar")
    assert product_in.name == "Test Product"
    assert product_in.price == 9.99
    assert product_in.description == "Foo Bar"

    assert product_in.model_dump() == {
        "name": "Test Product",
        "price": 9.99,
        "description": "Foo Bar",
    }


def test_product_schema_invalid_values():
    with pytest.raises(ValueError):
        Product(id=1, name="Test Product", price=-9.99, version=1)

    with pytest.raises(ValueError):
        Product(id=1, price=9.99, version=1, description="123")

    with pytest.raises(ValueError):
        Product(id=1, price=9.99, version="Version")


def test_product_in_schema_invalid_values():
    with pytest.raises(ValueError):
        ProductIn(name="Test Product", price=-9.99)

    with pytest.raises(ValueError):
        ProductIn(price=9.99, description="123")

    with pytest.raises(ValueError):
        ProductIn(price=9.99)
