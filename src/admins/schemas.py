from typing import Optional

from pydantic import BaseModel, ValidationError, validator

from admins.enums import TypeChoices
from admins.models import TemplateFieldChoices, TemplateField
from admins.utils import get_obj
from fastapi import HTTPException

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

    @validator("value")
    def validate_value(cls, value: Optional[dict], values: dict):
        template_field: TemplateField = await get_obj(TemplateField, values["template"]["id"])
        if template_field.type == TemplateFieldChoices.SELECT:
            if template_field.required and not value:
                raise HTTPException(status_code=400, detail={f"{values['label']}": "This field is required"})
            SelectDataSchema(**value)
        elif template_field.type == TemplateFieldChoices.STRING:
            if template_field.required and value["name"] == "":
                raise HTTPException(status_code=400, detail={f"{values['label']}": "This field is required"})
            NameSchema(**value)
        return value


class TemplateFieldAnswerSchemaReturn(BaseModel):
    id: int

    class Config:
        orm_mode = True
