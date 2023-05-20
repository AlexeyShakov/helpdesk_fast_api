from typing import Optional

from pydantic import BaseModel, ValidationError, validator

from admins.models import TemplateFieldChoices


class TopicSchemaCreate(BaseModel):
    name: str

class TopicSchemaReturn(TopicSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class CategorySchemaCreate(BaseModel):
    name: str
    topic: TopicSchemaReturn

class CategorySchemaReturn(CategorySchemaCreate):
    id: int

    class Config:
        orm_mode = True


class SelectDataSchema(BaseModel):
    name: str
    index: int

class TemplateFieldSchemaCreate(BaseModel):
    queue_index: int
    name: str
    required: bool
    type: TemplateFieldChoices
    data: Optional[dict] = None

    @validator("data")
    def validate_data(cls, value: Optional[dict], values: dict):
        if value == {}:
            raise ValueError("This field must not be {}")
        if values["type"] == TemplateFieldChoices.STRING:
            if value is not None:
                print("Я тут")
                raise ValueError("This field must be null")
        if values["type"] == TemplateFieldChoices.SELECT:
            SelectDataSchema(**value)
        return value


class TemplateFieldSchemaReturn(TemplateFieldSchemaCreate):
    id: int

    class Config:
        orm_mode = True
