import os
import uuid

import aiofiles
from fastapi import FastAPI, Request, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from admins.endpoints.categories import category_router
from admins.endpoints.ready_answers import ready_answers_router
from admins.endpoints.template_fields import template_fields_router
from admins.endpoints.templates import template_router
from admins.endpoints.topics import topic_router
from authentication import BasicAuthBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from config import FILE_STORAGE
from crud_handler import BaseHandler
from database import get_async_session
from staff.endpoints import group_router, user_router
from tickets.endpoints import ticket_router, ticket_file_router
from tickets.models import TicketFile
from tickets.schemas import TicketFileSchemaReturn


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
app.include_router(user_router)

app.include_router(ticket_router)

TICKET_FILE_ROUTE = "/api/ticket_files"
@app.post(f"{TICKET_FILE_ROUTE}/", response_model=TicketFileSchemaReturn, status_code=201)
async def upload_file(incoming_file: UploadFile, session: AsyncSession = Depends(get_async_session)):
    file_name = uuid.uuid4().hex[:6] + "_" + incoming_file.filename
    async with aiofiles.open(file_name, 'wb') as file:
        content = await incoming_file.read()
        await file.write(content)
    handler = BaseHandler(TicketFile)
    return await handler.create(session, {"path": os. getcwd(), "name": incoming_file.filename},
                                object_name="TicketFile", alchemy_model=TicketFile)
