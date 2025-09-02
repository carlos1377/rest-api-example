from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="REST API Products", version="1.0.0")


@app.get("/", status_code=200)
def read_root() -> dict[str, str]:
    return {"message": "Hello World!"}


app.include_router(router)
