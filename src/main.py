from fastapi import FastAPI
from admins.endpoints import router_section, router_topic

app = FastAPI()

app.include_router(router_section)
app.include_router(router_topic)
