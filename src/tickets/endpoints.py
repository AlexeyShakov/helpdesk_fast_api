from typing import List

from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admins.models import Category, Topic, TemplateField, TemplateFieldAnswer
from crud_handler import BaseHandler
from database import get_async_session
from fastapi import Depends

from tickets.models import Ticket
from tickets.schemas import TicketSchemaReturn, TicketSchemaCreate
from tickets.utils import check_answers

ticket_router = InferringRouter(tags=["Ticket"])
ROUTE = "/api/tickets"


@cbv(ticket_router)
class TicketView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Ticket)

    @ticket_router.post(f"{ROUTE}/", response_model=TicketSchemaReturn, status_code=201)
    async def create_item(self, ticket_object: TicketSchemaCreate):
        ticket_dict = ticket_object.dict()
        answers_data = ticket_dict.pop("answers")

        for el in answers_data:
            check_answers(el)

        category_object = await self.get_obj(select(Category), self.session, ticket_dict.get("category").get("id"))
        topic = await self.get_obj(select(Topic), self.session, ticket_dict.get("topic").get("id"))

        ticket_dict["topic"] = topic
        ticket_dict["category"] = category_object
        ticket = await self.create(self.session, ticket_dict, object_name="User")

        answer_objects = []
        for answer in answers_data:
            template_field_object = await self.get_obj(select(TemplateField), self.session,
                                                       answer.get("template_field").get("id"))
            answer["template_field"] = template_field_object
            answer["ticket"] = ticket
            answer_objects.append(
                await self.create(self.session, answer, TemplateFieldAnswer, object_name="User")
            )
        ticket.answers = answer_objects
        return ticket

    @ticket_router.get(f"{ROUTE}/", response_model=List[TicketSchemaReturn], status_code=200)
    async def read_tickets(self, offset: int = 0, limit: int = 2):
        query = select(self.model).options(selectinload(self.model.answers))
        return await self.list(query=query, session=self.session, limit=limit, offset=offset)

    @ticket_router.get(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=200)
    async def read_ticket(self, ticket_id: int):
        query = select(self.model).options(selectinload(self.model.answers))
        return await self.retrieve(query, self.session, ticket_id)

    @ticket_router.delete(f"{ROUTE}/" + "{ticket_id}", status_code=204)
    async def delete_ticket(self, ticket_id: int):
        return await self.delete(self.session, ticket_id)


    # НУЖНО ПРОВЕРИТЬ
    # @ticket_router.put(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=200)
    # async def update_topic(self, ticket_id: int, topic: TicketSchemaReturn):
    #     return await self.update(self.session, ticket_id, topic.dict())
