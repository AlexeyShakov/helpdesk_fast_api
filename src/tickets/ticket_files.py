import os
import uuid
from fastapi.responses import FileResponse
import aiofiles
from fastapi import UploadFile, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud_handler import BaseHandler
from database import get_async_session
from tickets.models import TicketFile
from tickets.schemas import TicketFileSchemaReturn

TICKET_FILE_ROUTE = "/api/ticket_files"
ticket_file_router = APIRouter(
    prefix="/api/ticket_files",
    tags=["TicketFile"]
)


@ticket_file_router.post("/", response_model=TicketFileSchemaReturn, status_code=201,
                         tags=["TicketFile"])
async def upload_file(incoming_file: UploadFile, session: AsyncSession = Depends(get_async_session)):
    file_name = uuid.uuid4().hex[:6] + "_" + incoming_file.filename
    file_path = os.path.join(os.getcwd(), "..\\", "file_storage", file_name)
    async with aiofiles.open(file_path, 'wb') as file:
        content = await incoming_file.read()
        await file.write(content)
    handler = BaseHandler(TicketFile)
    return await handler.create(session, {"path": file_path, "name": incoming_file.filename},
                                object_name="TicketFile", alchemy_model=TicketFile)


@ticket_file_router.get("/{ticket_file_id}", response_model=None, status_code=200,
                        tags=["TicketFile"])
async def download_file(
        ticket_file_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> FileResponse:
    query = select(TicketFile)
    handler = BaseHandler(TicketFile)
    ticket_file = await handler.get_obj(query, session, {"id": ticket_file_id})
    return FileResponse(ticket_file.path, filename=ticket_file.name, media_type='multipart/form-data')


@ticket_file_router.delete("/{ticket_file_id}", response_model=None, status_code=204,
                           tags=["TicketFile"])
async def delete_ticket_file(ticket_file_id: int, session: AsyncSession = Depends(get_async_session)) -> None:
    await _delete_file(ticket_file_id, session)


async def _delete_file(ticket_file_id: int, session: AsyncSession = Depends(get_async_session)):
    handler = BaseHandler(TicketFile)
    file_obj = await handler.get_obj(select(TicketFile), session, {"id": ticket_file_id})
    os.remove(file_obj.path)
    await session.delete(file_obj)
    await session.commit()
