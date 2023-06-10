from fastapi import APIRouter, Depends

from .schemas import CategorySchemaReturn, CategorySchemaCreate, \
    TemplateFieldSchemaReturn, TemplateFieldSchemaCreate, TemplateSchemaReturn, TemplateSchemaCreate, \
    TemplateFieldAnswerSchemaReturn, TemplateFieldAnswerSchemaCreate, \
    CategoryOrderingSchema, TemplateOrderingSchema, SearchingSchema
from .crud import create, get_list, get_object, delete_object, update_object_put, get_fields_by_template
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Topic, Category, TemplateField, Template, TemplateFieldAnswer
from typing import List

from database import get_async_session
from .utils import get_obj, validate_template_field_answer_value

router_template_field = APIRouter(
    prefix="/api/template_fields",
    tags=["TemplateField"]
)

router_template_field_answer = APIRouter(
    prefix="/api/template_field_answers",
    tags=["TemplateFieldAnswer"]
)




# @router_template.get("/{template_id}/template_fields", response_model=List[TemplateFieldSchemaReturn], status_code=200)
# async def fields_by_template(template_id: int, session: AsyncSession = Depends(get_async_session)):
#     return await get_fields_by_template(session, template_id)


# TemplateField endpoints
@router_template_field.post("/", response_model=TemplateFieldSchemaReturn, status_code=201)
async def create_template_field(template_field_object: TemplateFieldSchemaCreate,
                                session: AsyncSession = Depends(get_async_session)):
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


@router_template_field.put("/{template_field_id}", response_model=TemplateFieldSchemaReturn, status_code=200, )
async def update_put_template_field(template_field_id: int, template_field: TemplateFieldSchemaReturn,
                                    session: AsyncSession = Depends(get_async_session)):
    template_field_dict = template_field.dict()
    template_data = template_field_dict.pop("template")
    fk_obj = {"template_id": template_data["id"]}
    return await update_object_put(TemplateField, session, template_field_id, template_field_dict, fk_obj, True)


# TemplateFieldAnswer endpoints
@router_template_field_answer.post("/", response_model=TemplateFieldAnswerSchemaReturn, status_code=201)
async def create_template_field_answer(template_field_answer_object: TemplateFieldAnswerSchemaCreate,
                                       session: AsyncSession = Depends(get_async_session)):
    template_field_answer_dict = template_field_answer_object.dict()
    obj: TemplateField = await get_obj(TemplateField, session,
                                       template_field_answer_dict.get("template_field").get("id"))
    # Делаем проверку на поля
    await validate_template_field_answer_value(obj,
                                               template_field_answer_dict["value"],
                                               template_field_answer_dict["label"]
                                               )
    template_field_answer_dict["template_field"] = obj
    return await create(TemplateFieldAnswer, session, template_field_answer_dict)


@router_template_field_answer.get("/", response_model=List[TemplateFieldAnswerSchemaReturn], status_code=200)
async def read_template_field_answers(session: AsyncSession = Depends(get_async_session), offset: int = 0,
                                      limit: int = 2):
    return await get_list(TemplateFieldAnswer, session, offset, limit)


@router_template_field_answer.get("/{template_field_answer_id}", response_model=TemplateFieldAnswerSchemaReturn,
                                  status_code=200)
async def read_template_field_answer(template_field_answer_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(TemplateFieldAnswer, session, template_field_answer_id)


@router_template_field_answer.delete("/{template_field_answer_id}", status_code=204)
async def delete_template_field_answer(template_field_answer_id: int,
                                       session: AsyncSession = Depends(get_async_session)):
    return await delete_object(TemplateFieldAnswer, session, template_field_answer_id)


@router_template_field_answer.put("/{template_field_answer_id}", response_model=TemplateFieldAnswerSchemaReturn,
                                  status_code=200, )
async def update_put_template_field_answer(template_field_answer_id: int,
                                           template_field_answer: TemplateFieldAnswerSchemaReturn,
                                           session: AsyncSession = Depends(get_async_session)):
    template_field_answer_dict = template_field_answer.dict()
    obj: TemplateField = await get_obj(TemplateField, session,
                                       template_field_answer_dict.get("template_field").get("id"))
    await validate_template_field_answer_value(obj,
                                               template_field_answer_dict["value"],
                                               template_field_answer_dict["label"]
                                               )
    fields_for_updating = {key: value for key, value in template_field_answer_dict.items() if key in ("id", "value")}
    return await update_object_put(TemplateFieldAnswer, session, template_field_answer_id, fields_for_updating)
