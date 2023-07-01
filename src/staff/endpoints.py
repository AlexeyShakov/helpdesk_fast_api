from typing import List

from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from crud_handler import BaseHandler
from database import get_async_session
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from staff.models import Group
from staff.schemas import GroupSchemaReturn, GroupSchemaCreate

group_router = InferringRouter(tags=["Group"])
ROUTE = "/api/groups"


@cbv(group_router)
class GroupView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Group)

    @group_router.post(f"{ROUTE}/", response_model=GroupSchemaReturn, status_code=201)
    async def create_item(self, group_object: GroupSchemaCreate):
        return await self.create(self.session, group_object.dict())

    @group_router.get(f"{ROUTE}/", response_model=List[GroupSchemaReturn], status_code=200)
    async def get_groups(self,
                         offset: int = 0,
                         limit: int = 5):
        query = select(self.model)
        return await self.list(query=query,
                               session=self.session,
                               limit=limit,
                               offset=offset)

    @group_router.get(f"{ROUTE}/" + "{group_id}", response_model=GroupSchemaReturn, status_code=200)
    async def get_group(self, group_id: int):
        return await self.retrieve(self.session, group_id)

    @group_router.delete(f"{ROUTE}/" + "{group_id}", status_code=204)
    async def delete_group(self, group_id: int):
        return await self.delete(self.session, group_id)

    @group_router.put(f"{ROUTE}/" + "{group_id}", response_model=GroupSchemaReturn, status_code=200)
    async def update_topic(self, group_id: int, group: GroupSchemaReturn):
        return await self.update(self.session, group_id, group.dict())
