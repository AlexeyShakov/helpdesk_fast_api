from typing import Optional, List, Union
from datetime import datetime
from fastapi import HTTPException
from pydantic import validator
from pydantic import BaseModel

from admins.schemas import TopicSchemaForTicket, CategorySchemaForTicket, \
    TemplateFieldSchemaReturn
from staff.schemas import UserSchemaReturn
from tickets.enums import TicketStatusChoice, GradeChoice


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


class TicketFileSchemaReturn(BaseModel):
    id: int
    path: str
    name: str

    class Config:
        orm_mode = True


class MessageSchemaReturn(BaseModel):
    id: int
    text: str
    time: datetime
    author: UserSchemaReturn

    class Config:
        orm_mode = True


class TicketBaseSchema(BaseModel):
    title: str
    description: str
    topic: TopicSchemaForTicket
    category: CategorySchemaForTicket


class TicketSchemaCreate(TicketBaseSchema):
    answers: Optional[List[TemplateFieldAnswersSchemaCreate]]
    ticket_files: Optional[List[TicketFileSchemaReturn]]

    @validator("answers")
    def validate_data(cls, value: Optional[dict]) -> Union[dict, list]:
        if not value:
            return []
        for el in value:
            answer_data = el.dict()
            template_field = answer_data.get("template_field")
            if template_field["required"] and (not answer_data["value"] or not answer_data["value"]["name"]):
                raise HTTPException(status_code=500, detail=f"This field \"{answer_data['label']}\" is required")
            return value


class TicketSchemaOnlyID(BaseModel):
    id: int


class TicketSchemaReturn(TicketBaseSchema, TicketSchemaOnlyID):
    answers: List[TemplateFieldAnswersSchemaReturn]
    creator: UserSchemaReturn
    specialist: Optional[UserSchemaReturn] = None
    ticket_files: Optional[List[TicketFileSchemaReturn]]
    created: datetime
    in_work_date: Optional[datetime]
    status: TicketStatusChoice
    messages: Optional[List[MessageSchemaReturn]]
    grade: Optional[GradeChoice]

    class Config:
        orm_mode = True


class AssignSpecialistSchema(BaseModel):
    id: int


class MessageSchemaCreate(BaseModel):
    text: str


class GradeSchema(BaseModel):
    grade: GradeChoice
