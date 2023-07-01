from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from admins.models import Category, Topic
from crud_handler import BaseHandler
from database import get_async_session
from fastapi import Depends

from staff.models import User
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

        category_object = await self.get_obj(Category, self.session, ticket_dict.get("category").get("id"))
        topic = await self.get_obj(Topic, self.session, ticket_dict.get("topic").get("id"))

        ticket_dict["topic"] = topic
        ticket_dict["category"] = category_object
        return await self.create(self.session, ticket_dict, object_name="User")
