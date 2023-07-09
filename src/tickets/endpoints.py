import uuid
from typing import List

import aiofiles
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from admins.models import Category, Topic, TemplateField, TemplateFieldAnswer

from crud_handler import BaseHandler
from database import get_async_session
from fastapi import Depends, Request, HTTPException, UploadFile

from staff.models import User
from tickets.models import Ticket, TicketFile
from tickets.schemas import TicketSchemaReturn, TicketSchemaCreate, TicketFileSchemaReturn
from tickets.ticket_files import _delete_file

ticket_router = InferringRouter(tags=["Ticket"])
ROUTE = "/api/tickets"


@cbv(ticket_router)
class TicketView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Ticket)

    @ticket_router.post(f"{ROUTE}/", response_model=TicketSchemaReturn, status_code=201)
    async def create_item(self, ticket_object: TicketSchemaCreate, request: Request):
        ticket_dict = ticket_object.dict()
        answers_data = ticket_dict.pop("answers")
        files_data = ticket_dict.pop("ticket_files")

        category_object = await self.get_obj(select(Category), self.session,
                                             {"id": ticket_dict.get("category").get("id")})
        topic = await self.get_obj(select(Topic), self.session, {"id": ticket_dict.get("topic").get("id")})

        ticket_dict["topic"] = topic
        ticket_dict["category"] = category_object
        ticket_dict["creator"] = await self._create_ticket_creator(request)
        ticket = await self.create(self.session, ticket_dict, object_name="User")

        if files_data:
            for file in files_data:
                await self._add_files_to_ticket(file, ticket)
        if answers_data:
            await self._add_answers_to_ticket(answers_data, ticket)
        # We cannot create an object and get access to related object at once(in this case it's reverse FK).
        # So we need to query one more time with join
        ticket_with_answers = select(self.model). \
            options(selectinload(self.model.answers)). \
            options(selectinload(self.model.ticket_files))
        return await self.get_obj(ticket_with_answers, self.session, {"id": ticket.id})

    @ticket_router.get(f"{ROUTE}/", response_model=List[TicketSchemaReturn], status_code=200)
    async def read_tickets(self, offset: int = 0, limit: int = 2):
        query = select(self.model).options(selectinload(self.model.answers))
        return await self.list(query=query, session=self.session, limit=limit, offset=offset)

    @ticket_router.get(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=200)
    async def read_ticket(self, ticket_id: int):
        query = select(self.model). \
            options(selectinload(self.model.answers)). \
            options(selectinload(self.model.ticket_files))
        return await self.retrieve(query, self.session, ticket_id)

    @ticket_router.delete(f"{ROUTE}/" + "{ticket_id}", status_code=204)
    async def delete_ticket(self, ticket_id: int):
        return await self.delete(self.session, ticket_id)

    @ticket_router.put(f"{ROUTE}/" + "{ticket_id}", response_model=TicketSchemaReturn, status_code=200)
    async def update_ticket(self, ticket_id: int, ticket: TicketSchemaReturn):
        ticket_dict = ticket.dict()
        ticket_dict.pop("creator")
        answers = ticket_dict.pop("answers")
        files = ticket_dict.pop("ticket_files")

        # Обновление готовых ответов и файлов
        ticket_query = select(self.model). \
            options(selectinload(self.model.answers)). \
            options(selectinload(self.model.ticket_files))
        ticket_obj = await self.get_obj(ticket_query, self.session, {"id": ticket_dict.get("id")})
        answers_from_ticket = ticket_obj.answers
        files_from_ticket = ticket_obj.ticket_files
        await self._update_ready_answers(answers_from_ticket, answers)
        await self._update_files(files_from_ticket, files, ticket_obj, self.session)

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
        ticket_with_related_models = select(self.model). \
            options(selectinload(self.model.answers)). \
            options(selectinload(self.model.ticket_files))
        await self.session.commit()
        return await self.get_obj(ticket_with_related_models, self.session, {"id": ticket.id})

    async def _update_files(self,
                            files: List[TicketFile],
                            incoming_files: list,
                            ticket: Ticket,
                            session: AsyncSession = Depends(get_async_session)):
        # Сначала проверим, что приходящие файлы равны существующим
        # Нужно найти файлы, которые удалили
        incoming_ids = {el["id"] for el in incoming_files}
        ids_from_ticket = {el.id for el in files}
        if incoming_ids != ids_from_ticket:
            files_for_deletion = ids_from_ticket - incoming_ids
            files_for_adding_to_ticket = incoming_ids - ids_from_ticket

            if files_for_deletion:
                for el in files_for_deletion:
                    await _delete_file(el, session)
            if files_for_adding_to_ticket:
                files_data = {el["id"]: el for el in incoming_files}
                for el in files_for_adding_to_ticket:
                    await self._add_files_to_ticket(files_data[el], ticket)

    async def _update_ready_answers(self, answers: List[TemplateFieldAnswer], incoming_answers: list) -> None:
        answers_from_ticket = {el.id: el for el in answers}
        for el in incoming_answers:
            answer_from_ticket = answers_from_ticket.get(el["id"])
            if answer_from_ticket.value != el["value"]:
                del el["template_field"]
                await self.update(
                    session=self.session,
                    id=answer_from_ticket.id,
                    data=el,
                    alchemy_model=TemplateFieldAnswer
                )

    async def _create_ticket_creator(self, request: Request) -> User:
        try:
            creator = await self.get_obj(select(User), self.session, {"main_id": request.user.id})
        except HTTPException:
            creator_dict = request.user.__dict__
            creator_dict["main_id"] = creator_dict["id"]
            del creator_dict["id"]
            creator = await self.create(self.session, creator_dict, object_name="User", alchemy_model=User)
        return creator

    async def _add_files_to_ticket(self, file: dict, ticket: Ticket) -> None:
        file_obj = await self.get_obj(select(TicketFile), self.session,
                                      {"id": file.get("id")})
        file_obj.ticket = ticket

    async def _add_answers_to_ticket(self, answers: list, ticket: Ticket) -> None:
        for answer in answers:
            template_field_object = await self.get_obj(select(TemplateField), self.session,
                                                       {"id": answer.get("template_field").get("id")})
            answer["template_field"] = template_field_object
            answer["ticket"] = ticket
            await self.create(self.session, answer, object_name="Answer", alchemy_model=TemplateFieldAnswer)
