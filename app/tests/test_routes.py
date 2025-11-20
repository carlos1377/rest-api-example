from fastapi.testclient import TestClient
from fastapi import status


def _reset_products(client: TestClient):
    res = client.get("/products")
    if res.status_code == status.HTTP_200_OK:
        for p in res.json()["data"]:
            client.delete(f"/products/{p['id']}")


def _create(client: TestClient, name="Banana", price=10.0):
    res = client.post("/products", json={"name": name, "price": price})
    assert res.status_code == status.HTTP_201_CREATED
    body = res.json()
    assert "Location" in res.headers
    assert res.headers["Location"] == f"/products/{body['id']}"
    return body


def _get(client: TestClient, id_: int, if_none_match: str | None = None):
    headers = {}
    if if_none_match is not None:
        headers["If-None-Match"] = if_none_match
    return client.get(f"/products/{id_}", headers=headers)


def test_list_products_initially_empty(client: TestClient):
    _reset_products(client)

    res = client.get("/products")
    assert res.status_code == status.HTTP_200_OK

    payload = res.json()
    assert payload["data"] == []
    assert payload["count"] == 0


def test_list_products_after_creates(client: TestClient):
    _reset_products(client)

    p1 = _create(client, "Banana", 10.0)
    p2 = _create(client, "Maçã", 5.0)

    res = client.get("/products")
    assert res.status_code == status.HTTP_200_OK

    payload = res.json()
    ids = sorted([it["id"] for it in payload["data"]])
    assert ids == [p1["id"], p2["id"]]
    assert payload["count"] == 2


def test_create_product_returns_201_body_and_location(client: TestClient):
    _reset_products(client)

    res = client.post("/products", json={"name": "Banana", "price": 10.0})
    assert res.status_code == status.HTTP_201_CREATED

    body = res.json()
    assert body["id"] == 1
    assert body["version"] == 1
    assert body["name"] == "Banana"
    assert body["price"] == 10.0
    assert res.headers["Location"] == "/products/1"


def test_create_product_validates_payload_missing_price(client: TestClient):
    _reset_products(client)

    res = client.post("/products", json={"name": "SemPreço"})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_product_returns_200_and_sets_etag_header(client: TestClient):
    _reset_products(client)
    created = _create(client, "Banana", 10.0)

    res = _get(client, created["id"])
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == created

    assert "ETag" in res.headers
    etag = res.headers["ETag"]
    assert etag

    res2 = _get(client, created["id"], if_none_match=etag)
    assert res2.status_code == status.HTTP_304_NOT_MODIFIED

    assert res2.text == "null" or res2.text == ""


def test_get_product_404(client: TestClient):
    _reset_products(client)

    res = _get(client, 999)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_product_with_if_match_increments_version_and_updates_etag(
    client: TestClient,
):
    _reset_products(client)
    created = _create(client, "Banana", 10.0)

    first_get = _get(client, created["id"])
    old_etag = first_get.headers["ETag"]

    res = client.put(
        f"/products/{created['id']}",
        headers={"If-Match": '"1"'},
        json={"name": "Banana Prata", "price": 12.0},
    )
    assert res.status_code == status.HTTP_200_OK

    updated = res.json()
    assert updated["id"] == created["id"]
    assert updated["version"] == 2
    assert updated["name"] == "Banana Prata"
    assert updated["price"] == 12.0

    assert "ETag" in res.headers
    new_etag = res.headers["ETag"]
    assert new_etag and new_etag != old_etag

    res_after = _get(client, created["id"], if_none_match=old_etag)
    assert res_after.status_code == status.HTTP_200_OK
    assert res_after.json()["version"] == 2


def test_update_product_version_mismatch_returns_412(client: TestClient):
    _reset_products(client)
    created = _create(client, "Banana", 10.0)

    res = client.put(
        f"/products/{created['id']}",
        headers={"If-Match": '"999"'},
        json={"name": "X", "price": 9.9},
    )
    assert res.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert res.json()["detail"].lower().startswith("version mismatch")


def test_update_product_without_if_match_skips_lock_and_updates(
    client: TestClient,
):
    _reset_products(client)
    created = _create(client, "Banana", 10.0)

    res = client.put(
        f"/products/{created['id']}",
        json={"name": "SemLock", "price": 7.5},
    )
    assert res.status_code == status.HTTP_200_OK

    body = res.json()
    assert body["version"] == 2
    assert body["name"] == "SemLock"


def test_update_unknown_id_404(client: TestClient):
    _reset_products(client)

    res = client.put(
        "/products/9999",
        headers={"If-Match": '"1"'},
        json={"name": "Nada", "price": 1.0},
    )
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_existing_returns_204_and_then_404_on_get(client: TestClient):
    _reset_products(client)
    created = _create(client, "Banana", 10.0)

    res = client.delete(f"/products/{created['id']}")
    assert res.status_code == status.HTTP_204_NO_CONTENT

    res2 = _get(client, created["id"])
    assert res2.status_code == status.HTTP_404_NOT_FOUND


def test_delete_unknown_returns_404(client: TestClient):
    _reset_products(client)

    res = client.delete("/products/9999")
    assert res.status_code == status.HTTP_404_NOT_FOUND
