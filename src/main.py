from fastapi import FastAPI
from admins.endpoints import router as admins_router

app = FastAPI()

app.include_router(admins_router)
