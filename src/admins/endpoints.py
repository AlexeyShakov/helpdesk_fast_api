from fastapi import APIRouter, Depends
from .schemas import SectionSchemaCreate, SectionSchemaReturn, TopicReturn, TopicCreate
from .crud import create, get_list, get_object, delete_object, update_object_put
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Section, Topic
from typing import List

from database import get_async_session
from .utils import get_obj

router_section = APIRouter(
    prefix="/sections",
    tags=["Section"]
)

router_topic = APIRouter(
    prefix="/topics",
    tags=["Topic"]
)


@router_section.post("/", response_model=SectionSchemaReturn, status_code=201)
async def create_section(section_object: SectionSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(Section, session, section_object.dict())
@router_section.get("/", response_model=List[SectionSchemaReturn], status_code=200)
async def read_sections(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Section, session, offset, limit)

@router_section.get("/{section_id}", response_model=SectionSchemaReturn, status_code=200)
async def read_section(section_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Section, session, section_id)
@router_section.delete("/{section_id}", status_code=204)
async def delete_section(section_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Section, session, section_id)

@router_section.put("/{section_id}", response_model=SectionSchemaReturn, status_code=200)
async def update_put_section(section_id: int, section: SectionSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    return await update_object_put(Section, session, section_id, section.dict())

# Topic endpoints
@router_topic.post("/", response_model=TopicReturn, status_code=201)
async def create_topic(topic_object: TopicCreate, session: AsyncSession = Depends(get_async_session)):
    topic_dict = topic_object.dict()
    obj = await get_obj(Section, session, topic_dict.get("section").get("id"))
    topic_dict["section"] = obj
    return await create(Topic, session, topic_dict)

@router_topic.get("/", response_model=List[TopicReturn], status_code=200)
async def read_topics(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Topic, session, offset, limit)
@router_topic.get("/{topic_id}", response_model=TopicReturn, status_code=200)
async def read_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Topic, session, topic_id)

@router_topic.delete("/{topic_id}", status_code=204)
async def delete_topic(topic_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Topic, session, topic_id)

@router_topic.put("/{topic_id}", response_model=TopicReturn, status_code=200,)
async def update_put_topic(topic_id: int, topic: TopicReturn,session: AsyncSession = Depends(get_async_session)):
    topic_dict = topic.dict()
    section_data = topic_dict.pop("section")
    fk_obj = {"section_id": section_data["id"]}
    return await update_object_put(Topic, session, topic_id, topic_dict, fk_obj, True)
