from typing import Optional, List

from fastapi import HTTPException
from pydantic import validator
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
    answers: Optional[List[TemplateFieldAnswersSchemaCreate]]

    @validator("answers")
    def validate_data(cls, value: Optional[dict]) -> dict:
        if not value:
            return []
        for el in value:
            answer_data = el.dict()
            template_field = answer_data.get("template_field")
            if template_field["required"] and (not answer_data["value"] or not answer_data["value"]["name"]):
                raise HTTPException(status_code=500, detail=f"This field \"{answer_data['label']}\" is required")
            return value

class TicketSchemaReturn(TicketBaseSchema):
    id: int
    answers: List[TemplateFieldAnswersSchemaReturn]

    class Config:
        orm_mode = True
