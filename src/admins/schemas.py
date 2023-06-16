from typing import Optional

from pydantic import BaseModel, validator

from admins.enums import TypeChoices, TopicOrderingChoices, CategoryOrderingChoices, TemplateOrderingChoices
from admins.models import TemplateFieldChoices


class TopicSchemaCreate(BaseModel):
    name: str


class TopicSchemaReturn(TopicSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class TopicListSchemaReturn(TopicSchemaReturn):
    id: int
    category_count: int

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


class CategoryOnlyIDSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class CategorySchemaCreate(BaseModel):
    name: str
    topic: TopicSchemaReturn
    template: Optional[TemplateSchemaReturn]
    time_of_life: TimeSchema
    notification_repeat: TimeSchema


class CategorySchemaReturn(CategoryOnlyIDSchema, CategorySchemaCreate):
    pass


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


class ReadyAnswerSchemaCreate(BaseModel):
    answer_text: str
    category: CategoryOnlyIDSchema


class ReadyAnswerSchemaReturn(ReadyAnswerSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class TopicFilterSchema(BaseModel):
    name: Optional[str] = None
    has_categories: Optional[bool] = None


class TopicOrderingSchema(BaseModel):
    ordering: Optional[TopicOrderingChoices] = None


class CategoryOrderingSchema(BaseModel):
    ordering: Optional[CategoryOrderingChoices] = None


class TemplateOrderingSchema(BaseModel):
    ordering: Optional[TemplateOrderingChoices] = None


class SearchingSchema(BaseModel):
    search: Optional[str] = None


class TemplateFilterSchema(BaseModel):
    has_fields: Optional[bool] = None


class ReadyAnswerFilterSchema(BaseModel):
    category_id: Optional[int] = None
