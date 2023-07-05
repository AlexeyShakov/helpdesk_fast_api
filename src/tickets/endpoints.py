from typing import List

from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admins.models import Category, Topic, TemplateField
from crud_handler import BaseHandler
from database import get_async_session
from fastapi import Depends

from tickets.models import Ticket
from tickets.schemas import TicketSchemaReturn, TicketSchemaCreate, TemplateFieldAnswersSchemaReturn

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

        category_object = await self.get_obj(select(Category), self.session, ticket_dict.get("category").get("id"))
        topic = await self.get_obj(select(Topic), self.session, ticket_dict.get("topic").get("id"))

        ticket_dict["topic"] = topic
        ticket_dict["category"] = category_object
        ticket = await self.create(self.session, ticket_dict, object_name="User")

        if answers_data:
            for answer in answers_data:
                template_field_object = await self.get_obj(select(TemplateField), self.session,
                                                           answer.get("template_field").get("id"))
                answer["template_field"] = template_field_object
                answer["ticket"] = ticket
        # We cannot create an object and get access to related object at once(in this case it's reverse FK).
        # So we need to query one more time with join
        ticket_with_answers = select(self.model).options(selectinload(self.model.answers))
        return await self.get_obj(ticket_with_answers, self.session, ticket.id)

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

    @ticket_router.put(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=200)
    async def update_ticket(self, ticket_id: int, ticket: TicketSchemaReturn):
        ticket_dict = ticket.dict()
        ####
        # Доделать проверку того, что входящие поля ответов равны существуюущим
        # Как я буду проверять, что поля равны? Я прохожусь циклом по всем полям входящих ответов и собираю айдишки ответов из базы.
        # После этого по полученным айдишкам я получаю их из базы. Дальше я прохожусь еще раз циклом по входящим ответам  и сравниваю входящий объект и объект из базы
        ticket_query = select(self.model).options(selectinload(self.model.answers))
        ticket_obj = await self.get_obj(ticket_query, self.session, ticket_dict.get("id"))
        ####
        # Нужно сделать проверку, что если приходит другие данные в ответах, то мы должны их обновить
        answers = ticket_dict.pop("answers")
        topic_data = ticket_dict.pop("topic")
        category_data = ticket_dict.pop("category")
        fk_obj = {"topic_id": topic_data["id"], "category_id": category_data["id"]}
        ticket = await self.update(
            session=self.session,
            id=ticket_id,
            data=ticket_dict,
            fk_obj=fk_obj,
            update_fk=True
        )
        ticket_with_answers = select(self.model).options(selectinload(self.model.answers))
        return await self.get_obj(ticket_with_answers, self.session, ticket.id)
