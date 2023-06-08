from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from admins.ends.topics import new_topic_router
from admins.endpoints import router_category, router_template_field, router_template, \
    router_template_field_answer
from authentication import BasicAuthBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_auth_error)
]

app = FastAPI(middleware=middleware)

app.include_router(new_topic_router)
app.include_router(router_template)
app.include_router(router_category)
app.include_router(router_template_field)
app.include_router(router_template_field_answer)
