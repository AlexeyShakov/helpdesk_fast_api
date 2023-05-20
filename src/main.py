from fastapi import FastAPI
from admins.endpoints import router_category, router_topic, router_template_field, router_template

app = FastAPI()

app.include_router(router_topic)
app.include_router(router_template)
app.include_router(router_category)
app.include_router(router_template_field)
