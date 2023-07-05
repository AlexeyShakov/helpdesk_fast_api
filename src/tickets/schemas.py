from typing import Optional, List

from pydantic import BaseModel

from admins.schemas import TopicSchemaForTicket, CategorySchemaForTicket, \
    TemplateFieldSchemaReturn


class ValueSchema(BaseModel):
    name: str
    index: int


class TemplateFieldAnswersSchemaCreate(BaseModel):
    label: str
    value: Optional[ValueSchema]
    template_field: TemplateFieldSchemaReturn


class TemplateFieldAnswersSchemaReturn(TemplateFieldAnswersSchemaCreate):
    id: int
    template_field: TemplateFieldSchemaReturn

    class Config:
        orm_mode = True


class TicketBaseSchema(BaseModel):
    title: str
    description: str
    # creator: UserSchemaReturn
    topic: TopicSchemaForTicket
    category: CategorySchemaForTicket


class TicketSchemaCreate(TicketBaseSchema):
    answers: List[TemplateFieldAnswersSchemaCreate]


class TicketSchemaReturn(TicketBaseSchema):
    id: int
    answers: List[TemplateFieldAnswersSchemaReturn]

    class Config:
        orm_mode = True
