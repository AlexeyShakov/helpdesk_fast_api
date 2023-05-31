from fastapi import APIRouter, Depends, Request

from .filters import TopicFilter
from .schemas import TopicSchemaReturn, TopicSchemaCreate, CategorySchemaReturn, CategorySchemaCreate, \
    TemplateFieldSchemaReturn, TemplateFieldSchemaCreate, TemplateSchemaReturn, TemplateSchemaCreate, \
    TemplateFieldAnswerSchemaReturn, TemplateFieldAnswerSchemaCreate
from .crud import create, get_list, get_object, delete_object, update_object_put, get_fields_by_template
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Topic, Category, TemplateField, Template, TemplateFieldAnswer
from typing import List

from database import get_async_session
from .utils import get_obj, validate_template_field_answer_value


router_topic = APIRouter(
    prefix="/api/topics",
    tags=["Topic"]
)

router_category = APIRouter(
    prefix="/api/categories",
    tags=["Category"]
)

router_template = APIRouter(
    prefix="/api/templates",
    tags=["Template"]
)

router_template_field = APIRouter(
    prefix="/api/template_fields",
    tags=["TemplateField"]
)


router_template_field_answer = APIRouter(
    prefix="/api/template_field_answers",
    tags=["TemplateFieldAnswer"]
)


@router_topic.post("/", response_model=TopicSchemaReturn, status_code=201)
async def create_topic(topic_object: TopicSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(Topic, session, topic_object.dict())


@router_topic.get("/", response_model=List[TopicSchemaReturn], status_code=200)
async def read_topics(filter_params: TopicFilter = Depends(TopicFilter), session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Topic, session, filter_params.get_dict_with_values(), offset, limit)


@router_topic.get("/{topic_id}", response_model=TopicSchemaReturn, status_code=200)
async def read_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Topic, session, topic_id)


@router_topic.delete("/{topic_id}", status_code=204)
async def delete_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Topic, session, topic_id)

@router_topic.put("/{topic_id}", response_model=TopicSchemaReturn, status_code=200)
async def update_put_topic(topic_id: int, topic: TopicSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    return await update_object_put(Topic, session, topic_id, topic.dict())

# Category endpoints
@router_category.post("/", response_model=CategorySchemaReturn, status_code=201)
async def create_category(category_object: CategorySchemaCreate, session: AsyncSession = Depends(get_async_session)):
    category_dict = category_object.dict()
    topic_obj = await get_obj(Topic, session, category_dict.get("topic").get("id"))
    template_obj = await get_obj(Template, session, category_dict.get("template").get("id"))
    category_dict["topic"] = topic_obj
    category_dict["template"] = template_obj
    return await create(Category, session, category_dict)

@router_category.get("/", response_model=List[CategorySchemaReturn], status_code=200)
async def read_categories(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Category, session, offset, limit)

@router_category.get("/{category_id}", response_model=CategorySchemaReturn, status_code=200)
async def read_category(category_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Category, session, category_id)

@router_category.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Category, session, category_id)

@router_category.put("/{category_id}", response_model=CategorySchemaReturn, status_code=200,)
async def update_put_category(category_id: int, category: CategorySchemaReturn,session: AsyncSession = Depends(get_async_session)):
    category_dict = category.dict()
    topic_data = category_dict.pop("topic")
    template_data = category_dict.pop("template")
    fk_obj = {"topic_id": topic_data["id"], "template_id": template_data["id"]}
    return await update_object_put(Category, session, category_id, category_dict, fk_obj, True)

# Template endpoints
@router_template.post("/", response_model=TemplateSchemaReturn, status_code=201)
async def create_template_field(template_object: TemplateSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(Template, session, template_object.dict())

@router_template.get("/", response_model=List[TemplateSchemaReturn], status_code=200)
async def read_templates(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Template, session, offset, limit)


@router_template.get("/{template_id}", response_model=TemplateSchemaReturn, status_code=200)
async def read_template(template_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Template, session, template_id)


@router_template.delete("/{template_id}", status_code=204)
async def delete_category(template_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Template, session, template_id)


@router_template.put("/{template_id}", response_model=TemplateSchemaReturn, status_code=200)
async def update_put_topic(template_id: int, template: TemplateSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    return await update_object_put(Template, session, template_id, template.dict())

@router_template.get("/{template_id}/template_fields", response_model=List[TemplateFieldSchemaReturn], status_code=200)
async def fields_by_template(template_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_fields_by_template(session, template_id)


# TemplateField endpoints
@router_template_field.post("/", response_model=TemplateFieldSchemaReturn, status_code=201)
async def create_template_field(template_field_object: TemplateFieldSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    template_field_dict = template_field_object.dict()
    obj = await get_obj(Template, session, template_field_dict.get("template").get("id"))
    template_field_dict["template"] = obj
    return await create(TemplateField, session, template_field_dict)


@router_template_field.get("/", response_model=List[TemplateFieldSchemaReturn], status_code=200)
async def read_template_fields(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(TemplateField, session, offset, limit)


@router_template_field.get("/{template_field_id}", response_model=TemplateFieldSchemaReturn, status_code=200)
async def read_template_field(template_field_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(TemplateField, session, template_field_id)

@router_template_field.delete("/{template_field_id}", status_code=204)
async def delete_template_field(template_field_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(TemplateField, session, template_field_id)


@router_template_field.put("/{template_field_id}", response_model=TemplateFieldSchemaReturn, status_code=200,)
async def update_put_template_field(template_field_id: int, template_field: TemplateFieldSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    template_field_dict = template_field.dict()
    template_data = template_field_dict.pop("template")
    fk_obj = {"template_id": template_data["id"]}
    return await update_object_put(TemplateField, session, template_field_id, template_field_dict, fk_obj, True)


# TemplateFieldAnswer endpoints
@router_template_field_answer.post("/", response_model=TemplateFieldAnswerSchemaReturn, status_code=201)
async def create_template_field_answer(template_field_answer_object: TemplateFieldAnswerSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    template_field_answer_dict = template_field_answer_object.dict()
    obj: TemplateField = await get_obj(TemplateField, session, template_field_answer_dict.get("template_field").get("id"))
    # Делаем проверку на поля
    await validate_template_field_answer_value(obj,
                                               template_field_answer_dict["value"],
                                               template_field_answer_dict["label"]
                                               )
    template_field_answer_dict["template_field"] = obj
    return await create(TemplateFieldAnswer, session, template_field_answer_dict)


@router_template_field_answer.get("/", response_model=List[TemplateFieldAnswerSchemaReturn], status_code=200)
async def read_template_field_answers(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(TemplateFieldAnswer, session, offset, limit)


@router_template_field_answer.get("/{template_field_answer_id}", response_model=TemplateFieldAnswerSchemaReturn, status_code=200)
async def read_template_field_answer(template_field_answer_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(TemplateFieldAnswer, session, template_field_answer_id)


@router_template_field_answer.delete("/{template_field_answer_id}", status_code=204)
async def delete_template_field_answer(template_field_answer_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(TemplateFieldAnswer, session, template_field_answer_id)


@router_template_field_answer.put("/{template_field_answer_id}", response_model=TemplateFieldAnswerSchemaReturn, status_code=200,)
async def update_put_template_field_answer(template_field_answer_id: int, template_field_answer: TemplateFieldAnswerSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    template_field_answer_dict = template_field_answer.dict()
    obj: TemplateField = await get_obj(TemplateField, session, template_field_answer_dict.get("template_field").get("id"))
    await validate_template_field_answer_value(obj,
                                               template_field_answer_dict["value"],
                                               template_field_answer_dict["label"]
                                               )
    fields_for_updating = {key: value for key, value in template_field_answer_dict.items() if key in ("id", "value")}
    return await update_object_put(TemplateFieldAnswer, session, template_field_answer_id, fields_for_updating)
