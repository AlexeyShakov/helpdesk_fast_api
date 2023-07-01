from typing import List

from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from admins.models import Category
from crud_handler import BaseHandler
from database import get_async_session
from fastapi_utils.cbv import cbv
from sqlalchemy import select
from staff.models import Group, User
from staff.schemas import GroupSchemaReturn, GroupSchemaCreate, UserSchemaReturn, UserSchemaCreate

group_router = InferringRouter(tags=["Group"])
ROUTE = "/api/groups"

user_router = InferringRouter(tags=["User"])
ROUTE_USER = "/api/users"


@cbv(group_router)
class GroupView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Group)

    @group_router.post(f"{ROUTE}/", response_model=GroupSchemaReturn, status_code=201)
    async def create_item(self, group_object: GroupSchemaCreate):
        return await self.create(self.session, group_object.dict(), object_name="Group")

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


@cbv(user_router)
class UserView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(User)

    @user_router.post(f"{ROUTE_USER}/", response_model=UserSchemaReturn, status_code=201)
    async def create_item(self, user_object: UserSchemaCreate):
        user_dict = user_object.dict()
        group_obj = await self.get_obj(Group, self.session, user_dict.get("group").get("id"))
        category_object = await self.get_obj(Category, self.session, user_dict.get("category").get("id"))
        user_dict["group"] = group_obj
        user_dict["category"] = category_object
        return await self.create(self.session, user_dict, object_name="User")
