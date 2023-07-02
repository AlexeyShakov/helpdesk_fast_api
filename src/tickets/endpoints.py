from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv

from sqlalchemy.ext.asyncio import AsyncSession

from admins.models import Category, Topic, TemplateField, TemplateFieldAnswer
from crud_handler import BaseHandler
from database import get_async_session
from fastapi import Depends

from tickets.models import Ticket
from tickets.schemas import TicketSchemaReturn, TicketSchemaCreate

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

        category_object = await self.get_obj(Category, self.session, ticket_dict.get("category").get("id"))
        topic = await self.get_obj(Topic, self.session, ticket_dict.get("topic").get("id"))

        ticket_dict["topic"] = topic
        ticket_dict["category"] = category_object
        ticket = await self.create(self.session, ticket_dict, object_name="User")

        answer_objects = []
        for answer in answers_data:
            template_field_object = await self.get_obj(TemplateField, self.session,
                                                       answer.get("template_field"))
            answer["template_field"] = template_field_object
            answer["ticket"] = ticket
            obj = TemplateFieldAnswer(**answer)
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            answer_objects.append(obj)
        ticket.answers = answer_objects
        return ticket
