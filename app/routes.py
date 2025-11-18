from fastapi import APIRouter, Depends, Response, Header, HTTPException, status
from app.schemas import ListProductsResponse, CreateProductResponse, ProductIn
from app.services import ProductsService
from app.deps import get_products_service
from app.utils import make_etag


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ListProductsResponse)
def list_products(svc: ProductsService = Depends(get_products_service)):
    data = svc.list()
    return {"data": data, "count": len(data)}


@router.get("/{product_id}")
def get_product(
    product_id: int,
    response: Response,
    svc: ProductsService = Depends(get_products_service),
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
):
    product = svc.get(product_id)
    if not product:
        raise HTTPException(status_code=404)

    body = product.model_dump_json().encode()
    etag = make_etag(body)
    response.headers["ETag"] = etag
    if if_none_match == etag:
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return
    return product


@router.post("/", status_code=201, response_model=CreateProductResponse)
def create_product(
    product: ProductIn,
    response: Response,
    svc: ProductsService = Depends(get_products_service),
):
    created_product = svc.create(product)
    response.headers["Location"] = f"/products/{created_product.id}"
    return created_product


@router.put("/{product_id}")
def put_product(
    product_id: int,
    product: ProductIn,
    response: Response,
    svc: ProductsService = Depends(get_products_service),
    if_match: str | None = Header(default=None, alias="If-Match"),
):
    expected_version = None
    if if_match:
        try:
            expected_version = int(if_match.strip('"'))
        except ValueError:
            pass
    try:
        p = svc.update(product_id, product, expected_version)
    except ValueError:
        raise HTTPException(
            status_code=412, detail="Version mismatch (precondition failed)"
        )
    if not p:
        raise HTTPException(status_code=404)
    body = p.model_dump_json().encode()
    response.headers["ETag"] = make_etag(body)
    return p


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    svc: ProductsService = Depends(get_products_service),
):
    ok = svc.delete(product_id)
    if not ok:
        raise HTTPException(status_code=404)
