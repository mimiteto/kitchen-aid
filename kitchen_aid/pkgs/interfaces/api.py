#! /usr/bin/env python3

import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None) -> dict[str, str | int]:
    return {"item_id": item_id, "q": q or "MISSED"}

@app.post("/items/")
async def create_item(item: dict[str, str]) -> tuple[dict[str, str], int]:
    return item, 123

if __name__ == "__main__":
    uvicorn.run(
        app="api:app",
        host="0.0.0.0", port=9876, reload=False,
    )
