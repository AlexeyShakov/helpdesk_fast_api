from typing import List
from fastapi import Request
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admins.models import Category, Topic, Template
from permissions import manage_helpdesk
from admins.schemas import CategorySchemaReturn, CategorySchemaCreate, CategoryOrderingSchema, SearchingSchema
from crud_handler import BaseHandler
from database import get_async_session

category_router = InferringRouter(tags=["Сategory"])
ROUTE = "/api/categories"


@cbv(category_router)
class CategoryView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Category)

    @category_router.post(f"{ROUTE}", response_model=CategorySchemaReturn, status_code=201)
    async def create_category(self, category_object: CategorySchemaCreate, request: Request):
        category_dict = category_object.dict()
        topic_obj = await self.get_obj(select(Topic), self.session, {"id": category_dict.get("topic").get("id")})
        template_obj = await self.get_obj(select(Template), self.session,
                                          {"id": category_dict.get("template").get("id")})
        category_dict["topic"] = topic_obj
        category_dict["template"] = template_obj
        return await self.create(self.session, category_dict, object_name="Category")

    @category_router.get(f"{ROUTE}", response_model=List[CategorySchemaReturn], status_code=200)
    async def read_categories(
            self,
            ordering_params: CategoryOrderingSchema = Depends(CategoryOrderingSchema),
            searching_params: SearchingSchema = Depends(SearchingSchema),
            offset: int = 0,
            limit: int = 2
    ):
        search_fields = {
            "ordinary": {"column": "name"},
            "related": [{"table": Topic, "column": "name"}]
        }
        joined_ordering = {"related_table": Topic, "related_field_name": "topic", "ordering_field": "name"}
        query = select(self.model).join(Topic)
        return await self.list(
            query=query,
            session=self.session,
            ordering_params=ordering_params.dict(),
            joined_ordering=joined_ordering,
            searching_params=searching_params.dict(),
            search_fields=search_fields,
            limit=limit,
            offset=offset
        )

    @category_router.get(f"{ROUTE}/" + "{category_id}", response_model=CategorySchemaReturn, status_code=200)
    async def read_category(self, category_id: int, request: Request):
        query = select(self.model)
        return await self.retrieve(query, self.session, category_id)

    @category_router.delete(f"{ROUTE}/" + "{category_id}", status_code=204)
    async def delete_category(self, category_id: int, request: Request):
        return await self.delete(self.session, category_id)

    @category_router.put(f"{ROUTE}/" + "{category_id}", response_model=CategorySchemaReturn, status_code=200, )
    async def update_put_category(self, request: Request, category_id: int, category: CategorySchemaReturn):
        category_dict = category.dict()
        topic_data = category_dict.pop("topic")
        template_data = category_dict.pop("template")
        fk_obj = {"topic_id": topic_data["id"], "template_id": template_data["id"]}
        category_obj = await self.update(
            session=self.session,
            id=category_id,
            data=category_dict,
            fk_obj=fk_obj,
            update_fk=True
        )
        await self.session.commit()
        return category_obj
