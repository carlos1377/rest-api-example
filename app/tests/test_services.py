from app.schemas import ProductIn
import pytest


def _mk(name="Item", price=1.0) -> ProductIn:
    return ProductIn(name=name, price=price)


def test_create_increments_id_and_sets_version(service):
    p1 = service.create(_mk("A", 1.0))
    p2 = service.create(_mk("B", 2.0))

    assert p1.id == 1
    assert p2.id == 2
    assert p1.version == 1 and p2.version == 1
    assert p1.name == "A" and p2.name == "B"


def test_get_returns_same_object_data(service):
    created = service.create(_mk("A", 1.0))
    fetched = service.get(created.id)
    assert fetched == created


def test_get_unknown_id_returns_none(service):
    assert service.get(999) is None


def test_list_returns_all_products_with_stable_ids(populated_service):
    items = populated_service.list()
    ids = sorted([p.id for p in items])
    assert ids == [1, 2]
    names = {p.name for p in items}
    assert names == {"Banana", "Maçã"}


def test_update_happy_path_increments_version(populated_service):
    updated = populated_service.update(
        product_id=1,
        data=_mk("Banana Prata", 12.0),
        expected_version=1,
    )
    assert updated is not None
    assert updated.id == 1
    assert updated.version == 2
    assert updated.name == "Banana Prata"
    assert populated_service.get(1).version == 2


def test_update_unknown_id_returns_none(service):
    out = service.update(42, _mk("X", 9.9), expected_version=1)
    assert out is None


def test_update_version_mismatch_raises(populated_service):
    with pytest.raises(ValueError) as exc:
        populated_service.update(
            product_id=1,
            data=_mk("Qualquer", 99.0),
            expected_version=999,
        )
    assert "version_mismatch" in str(exc.value)
    assert populated_service.get(1).version == 1
    assert populated_service.get(1).name == "Banana"


def test_update_without_expected_version_skips_lock_check(populated_service):
    updated = populated_service.update(
        product_id=1,
        data=_mk("Banana (sem lock)", 11.0),
        expected_version=None,
    )
    assert updated is not None
    assert updated.version == 2
    assert updated.name == "Banana (sem lock)"


def test_delete_existing_returns_true_and_removes(populated_service):
    ok = populated_service.delete(1)
    assert ok is True
    assert populated_service.get(1) is None
    assert populated_service.get(2) is not None


def test_delete_unknown_returns_false(service):
    assert service.delete(12345) is False
