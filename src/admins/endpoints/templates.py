from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admins.filters import TemplateFilter
from admins.models import Template
from admins.schemas import TemplateSchemaCreate, TemplateSchemaReturn, TemplateOrderingSchema, SearchingSchema, \
    TemplateFilterSchema, TemplateFieldSchemaReturn
from admins.utils import get_fields_by_template
from crud_handler import BaseHandler
from database import get_async_session

template_router = InferringRouter(tags=["Template"])
ROUTE = "/api/templates"


@cbv(template_router)
class TemplateView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(Template, TemplateFilter)

    @template_router.post(f"{ROUTE}/", response_model=TemplateSchemaReturn, status_code=201)
    async def create_item(self, template_object: TemplateSchemaCreate):
        return await self.create(self.session, template_object.dict(), object_name="Template")

    @template_router.get(f"{ROUTE}/", response_model=List[TemplateSchemaReturn], status_code=201)
    async def get_templates(
            self,
            ordering_params: TemplateOrderingSchema = Depends(TemplateOrderingSchema),
            searching_params: SearchingSchema = Depends(SearchingSchema),
            filter_params: TemplateFilterSchema = Depends(TemplateFilterSchema),
            offset: int = 0,
            limit: int = 2
    ):
        search_fields = {
            "ordinary": {"column": "name"},
            "related": []
        }
        query = select(self.model)
        return await self.list(query=query,
                               session=self.session,
                               ordering_params=ordering_params.dict(),
                               searching_params=searching_params.dict(),
                               search_fields=search_fields,
                               filter_params=filter_params.dict(),
                               limit=limit,
                               offset=offset)

    @template_router.get(f"{ROUTE}/" + "{template_id}", response_model=TemplateSchemaReturn, status_code=200)
    async def read_template(self, template_id: int):
        return await self.retrieve(self.session, template_id)

    @template_router.delete(f"{ROUTE}/" + "{template_id}", status_code=204)
    async def delete_template(self, template_id: int):
        return await self.delete(self.session, template_id)

    @template_router.put(f"{ROUTE}/" + "{template_id}", response_model=TemplateSchemaReturn, status_code=200)
    async def update_template(self, template_id: int, template: TemplateSchemaReturn):
        return await self.update(self.session, template_id, template.dict())

    @template_router.get("/{template_id}/template_fields", response_model=List[TemplateFieldSchemaReturn], status_code=200)
    async def fields_by_template(self, template_id: int, session: AsyncSession = Depends(get_async_session)):
        return await get_fields_by_template(session, template_id)
