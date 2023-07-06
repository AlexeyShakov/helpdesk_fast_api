from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admins.models import TemplateField, Template
from admins.schemas import TemplateFieldSchemaCreate, TemplateFieldSchemaReturn
from crud_handler import BaseHandler
from database import get_async_session

template_fields_router = InferringRouter(tags=["TemplateFields"])
ROUTE = "/api/template_fields"


@cbv(template_fields_router)
class TemplateView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(TemplateField)

    @template_fields_router.post(f"{ROUTE}/", response_model=TemplateFieldSchemaReturn, status_code=201)
    async def create_item(self, template_field_object: TemplateFieldSchemaCreate):
        template_field_dict = template_field_object.dict()
        obj = await self.get_obj(select(Template), self.session, template_field_dict.get("template").get("id"))
        template_field_dict["template"] = obj
        return await self.create(self.session, template_field_dict)

    @template_fields_router.delete(f"{ROUTE}/" + "{template_field_id}", status_code=204)
    async def delete_template_field(self, template_field_id: int):
        return await self.delete(self.session, template_field_id)

    @template_fields_router.put(f"{ROUTE}/" + "{template_field_id}",
                                response_model=TemplateFieldSchemaReturn,
                                status_code=200)
    async def update_template_field(self, template_field_id: int, template_field: TemplateFieldSchemaReturn):
        template_field_dict = template_field.dict()
        template_data = template_field_dict.pop("template")
        fk_obj = {"template_id": template_data["id"]}
        template_field_obj = await self.update(
            session=self.session,
            id=template_field_id,
            data=template_field_dict,
            fk_obj=fk_obj,
            update_fk=True
        )
        await self.session.commit()
        return template_field_obj
