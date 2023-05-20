from fastapi import APIRouter, Depends
from .schemas import TopicSchemaReturn, TopicSchemaCreate, CategorySchemaReturn, CategorySchemaCreate, \
    TemplateFieldSchemaReturn, TemplateFieldSchemaCreate
from .crud import create, get_list, get_object, delete_object, update_object_put
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Topic, Category, TemplateField
from typing import List

from database import get_async_session
from .utils import get_obj

router_topic = APIRouter(
    prefix="/topics",
    tags=["Topic"]
)

router_category = APIRouter(
    prefix="/categories",
    tags=["Category"]
)

router_template_field = APIRouter(
    prefix="/template_fields",
    tags=["TemplateField"]
)


@router_topic.post("/", response_model=TopicSchemaReturn, status_code=201)
async def create_topic(topic_object: TopicSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(Topic, session, topic_object.dict())


@router_topic.get("/", response_model=List[TopicSchemaReturn], status_code=200)
async def read_topic(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Topic, session, offset, limit)


@router_topic.get("/{topic_id}", response_model=TopicSchemaReturn, status_code=200)
async def read_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Topic, session, topic_id)


@router_topic.delete("/{topic_id}", status_code=204)
async def delete_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Topic, session, topic_id)

@router_topic.put("/{topic_id}", response_model=TopicSchemaReturn, status_code=200)
async def update_put_section(topic_id: int, topic: TopicSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    return await update_object_put(Topic, session, topic_id, topic.dict())

# Category endpoints
@router_category.post("/", response_model=CategorySchemaReturn, status_code=201)
async def create_topic(category_object: CategorySchemaCreate, session: AsyncSession = Depends(get_async_session)):
    category_dict = category_object.dict()
    obj = await get_obj(Topic, session, category_dict.get("topic").get("id"))
    category_dict["topic"] = obj
    return await create(Category, session, category_dict)

@router_category.get("/", response_model=List[CategorySchemaReturn], status_code=200)
async def read_categories(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Category, session, offset, limit)
@router_category.get("/{category_id}", response_model=CategorySchemaReturn, status_code=200)
async def read_topic(category_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Category, session, category_id)

@router_category.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Category, session, category_id)

@router_category.put("/{category_id}", response_model=CategorySchemaReturn, status_code=200,)
async def update_put_category(category_id: int, category: CategorySchemaReturn,session: AsyncSession = Depends(get_async_session)):
    category_dict = category.dict()
    topic_data = category_dict.pop("topic")
    fk_obj = {"topic_id": topic_data["id"]}
    return await update_object_put(Category, session, category_id, category_dict, fk_obj, True)

# TemplateField endpoints
@router_template_field.post("/", response_model=TemplateFieldSchemaReturn, status_code=201)
async def create_template_field(template_field_object: TemplateFieldSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(TemplateField, session, template_field_object.dict())
