from typing import TYPE_CHECKING, Any, Callable, get_type_hints, List

from fastapi import Depends, APIRouter

from admins.schemas import TopicSchemaReturn, TopicSchemaCreate, TopicOrderingSchema
from crud_handler import BaseHandler
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Topic

##########
# class InferringRouter(APIRouter):
#     """
#     Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
#     """
#
#     if not TYPE_CHECKING:  # pragma: no branch
#
#         def add_api_route(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
#             if kwargs.get("response_model") is None:
#                 print("шо")
#                 kwargs["response_model"] = get_type_hints(endpoint).get("return")
#             return super().add_api_route(path, endpoint, **kwargs)
# ############################3

new_topic_router = InferringRouter(tags=["Topic"])
ROUTE = "/api/topics"


@cbv(new_topic_router)
class TopicView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Topic)

    @new_topic_router.post(f"{ROUTE}/", response_model=TopicSchemaReturn, status_code=201)
    async def create_item(self, topic_object: TopicSchemaCreate):
        return await self.create(self.session, topic_object.dict())

    @new_topic_router.get(f"{ROUTE}/", response_model=List[TopicSchemaReturn], status_code=200)
    async def get_topics(self, ordering_params: TopicOrderingSchema = Depends(TopicOrderingSchema),):
        return await self.list(self.session, ordering_params=ordering_params.dict())

    @new_topic_router.get(f"{ROUTE}/" + "{topic_id}", response_model=TopicSchemaReturn, status_code=200)
    async def get_topic(self, topic_id: int):
        return await self.retrieve(self.session, topic_id)

    @new_topic_router.delete(f"{ROUTE}/" + "{topic_id}", status_code=204)
    async def delete_topic(self, topic_id: int):
        return await self.delete(self.session, topic_id)

    @new_topic_router.put(f"{ROUTE}/" + "{topic_id}", response_model=TopicSchemaReturn, status_code=200)
    async def update_topic(self, topic_id: int, topic: TopicSchemaReturn):
        return await self.update(self.session, topic_id, topic.dict())
