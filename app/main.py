from fastapi import FastAPI
from .db import connect_to_mongo, disconnect_from_mongo
from .employees_router import router as employees_router

app = FastAPI(title="Employee API", version="1.0.0")

app.include_router(employees_router)


@app.on_event("startup")
async def _startup() -> None:
    await connect_to_mongo()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await disconnect_from_mongo()