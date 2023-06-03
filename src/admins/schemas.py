from typing import Optional

from pydantic import BaseModel, ValidationError, validator

from admins.enums import TypeChoices, TopicOrderingChoices
from admins.models import TemplateFieldChoices, TemplateField


class TopicSchemaCreate(BaseModel):
    name: str

class TopicSchemaReturn(TopicSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class TemplateSchemaCreate(BaseModel):
    name: str


class TemplateSchemaReturn(TemplateSchemaCreate):
    id: int
    # Нужно еще как-то возвращать все TemplateField, связанные с Template
    class Config:
        orm_mode = True


class TimeSchema(BaseModel):
    value: int
    type: TypeChoices


class CategorySchemaCreate(BaseModel):
    name: str
    topic: TopicSchemaReturn
    template: Optional[TemplateSchemaReturn]
    time_of_life: TimeSchema
    notification_repeat: TimeSchema

class CategorySchemaReturn(CategorySchemaCreate):
    id: int

    class Config:
        orm_mode = True


class NameSchema(BaseModel):
    name: str

class SelectDataSchema(NameSchema):
    index: int




class TemplateFieldSchemaCreate(BaseModel):
    queue_index: int
    name: str
    required: bool
    type: TemplateFieldChoices
    data: Optional[dict] = None
    template: TemplateSchemaReturn

    @validator("data")
    def validate_data(cls, value: Optional[dict], values: dict):
        if value == {}:
            raise ValueError("This field must not be {}")
        if values["type"] == TemplateFieldChoices.STRING:
            if value is not None:
                raise ValueError("This field must be null")
        if values["type"] == TemplateFieldChoices.SELECT:
            SelectDataSchema(**value)
        return value


class TemplateFieldSchemaReturn(TemplateFieldSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class TemplateFieldAnswerSchemaCreate(BaseModel):
    template_field: TemplateFieldSchemaReturn
    label: str
    value: dict


class TemplateFieldAnswerSchemaReturn(TemplateFieldAnswerSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class TopicFilterSchema(BaseModel):
    name: Optional[str] = None
    has_categories: Optional[bool] = None


class TopicOrderingSchema(BaseModel):
    ordering: Optional[TopicOrderingChoices] = None