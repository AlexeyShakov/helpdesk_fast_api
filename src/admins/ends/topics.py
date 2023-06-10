from typing import TYPE_CHECKING, Any, Callable, get_type_hints, List, Optional

from fastapi import Depends, APIRouter

from admins.filters import TopicFilter
from admins.schemas import TopicSchemaReturn, TopicSchemaCreate, TopicOrderingSchema, TopicFilterSchema
from crud_handler import BaseHandler
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Topic

topic_router = InferringRouter(tags=["Topic"])
ROUTE = "/api/topics"


@cbv(topic_router)
class TopicView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Topic, TopicFilter)

    @topic_router.post(f"{ROUTE}/", response_model=TopicSchemaReturn, status_code=201)
    async def create_item(self, topic_object: TopicSchemaCreate):
        return await self.create(self.session, topic_object.dict())

    @topic_router.get(f"{ROUTE}/", response_model=List[TopicSchemaReturn], status_code=200)
    async def get_topics(self,
                         ordering_params: TopicOrderingSchema = Depends(TopicOrderingSchema),
                         filter_params: TopicFilterSchema = Depends(TopicFilterSchema),
                         offset: int = 0,
                         limit: int = 5):
        return await self.list(session=self.session,
                               ordering_params=ordering_params.dict(),
                               filter_params=filter_params.dict(),
                               limit=limit,
                               offset=offset)

    @topic_router.get(f"{ROUTE}/" + "{topic_id}", response_model=TopicSchemaReturn, status_code=200)
    async def get_topic(self, topic_id: int):
        return await self.retrieve(self.session, topic_id)

    @topic_router.delete(f"{ROUTE}/" + "{topic_id}", status_code=204)
    async def delete_topic(self, topic_id: int):
        return await self.delete(self.session, topic_id)

    @topic_router.put(f"{ROUTE}/" + "{topic_id}", response_model=TopicSchemaReturn, status_code=200)
    async def update_topic(self, topic_id: int, topic: TopicSchemaReturn):
        return await self.update(self.session, topic_id, topic.dict())
