from typing import Optional

from pydantic import BaseModel

from admins.schemas import TopicSchemaReturn, CategorySchemaReturn, TopicSchemaForTicket, CategorySchemaForTicket
from staff.schemas import UserSchemaReturn
from tickets.enums import TicketStatusChoice, GradeChoice


class TicketSchemaCreate(BaseModel):
    title: str
    description: str
    # creator: UserSchemaReturn
    topic: TopicSchemaForTicket
    category: CategorySchemaForTicket


class TicketSchemaReturn(TicketSchemaCreate):
    id: int

    class Config:
        orm_mode = True
