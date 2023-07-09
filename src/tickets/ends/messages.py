from fastapi import Depends, Request
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from crud_handler import BaseHandler
from database import get_async_session
from staff.models import User
from tickets.models import Message, Ticket
from tickets.schemas import MessageSchemaCreate, TicketSchemaReturn

message_router = InferringRouter(tags=["Message"])
ROUTE = "/api/messages"


@cbv(message_router)
class TicketView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Message)

    @message_router.post(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=201)
    async def create_item(self, ticket_id: int, request: Request, input_data: MessageSchemaCreate):
        handler = BaseHandler(Message)
        author = await self.get_obj(select(User), self.session, {"main_id": request.user.id})
        ticket_query = select(Ticket). \
            options(selectinload(Ticket.answers)). \
            options(selectinload(Ticket.ticket_files)). \
            options(selectinload(Ticket.messages))
        ticket = await handler.get_obj(ticket_query, self.session, {"id": ticket_id})
        message_dict = {
            "text": input_data.text,
            "author": author,
            "ticket": ticket
        }
        await self.create(self.session, message_dict, object_name="Message")
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

    @message_router.delete(f"{ROUTE}/" + "{message_id}", response_model=TicketSchemaReturn, status_code=200)
    async def delete_item(self, message_id: int):
        message_query = select(self.model).options(selectinload(self.model.ticket).
                                                   options(selectinload(Ticket.answers)).
                                                   options(selectinload(Ticket.ticket_files)).
                                                   options(selectinload(Ticket.messages))
                                                   )
        message = await self.get_obj(message_query, self.session, {"id": message_id})
        print("message", message.id)
        ticket = message.ticket
        await self.delete(self.session, message_id)
        await self.session.refresh(ticket)
        return ticket

    @message_router.put(f"{ROUTE}/" + "{message_id}", response_model=TicketSchemaReturn, status_code=200)
    async def update_item(self, message_id, input_data: MessageSchemaCreate):
        message_query = select(self.model).options(selectinload(self.model.ticket).
                                                   options(selectinload(Ticket.answers)).
                                                   options(selectinload(Ticket.ticket_files)).
                                                   options(selectinload(Ticket.messages))
                                                   )
        # I don't know why here I need to wrap message_id in "int" but in "delete_item" I am not supposed to do that
        message = await self.get_obj(message_query, self.session, {"id": int(message_id)})
        message.text = input_data.text
        ticket = message.ticket
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket
