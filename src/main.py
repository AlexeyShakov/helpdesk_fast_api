from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from admins.endpoints.categories import category_router
from admins.endpoints.ready_answers import ready_answers_router
from admins.endpoints.template_fields import template_fields_router
from admins.endpoints.templates import template_router
from admins.endpoints.topics import topic_router
from authentication import BasicAuthBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from staff.endpoints import group_router


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_auth_error)
]

app = FastAPI(middleware=middleware)

app.include_router(topic_router)
app.include_router(template_router)
app.include_router(category_router)
app.include_router(template_fields_router)
app.include_router(ready_answers_router)

app.include_router(group_router)
