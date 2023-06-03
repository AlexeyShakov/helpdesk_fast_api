from admins.filters import FilterExample
from admins.models import TemplateField
from admins.utils import get_obj
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from sqlalchemy import update, exc
from fastapi import HTTPException
from sqlalchemy import or_

from admins import filters

async def create(model: Base, session: AsyncSession, data: dict) -> Base:
    obj = model(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_list(model: Base,filter_class_name: str, session: AsyncSession, filter_params: dict, offset: int = 0, limit: int = 2) -> Sequence:
    if any([v for k, v in filter_params.items()]):
        filter_class = getattr(filters, filter_class_name)
        filter_instance = filter_class(**filter_params)
        query = filter_instance.process_filtering(filter_instance.__dict__)
    else:
        query = select(model)
    result = await session.execute(query)
    return result.scalars().all()

async def get_object(model: Base, session: AsyncSession, id: int) -> Base:
    return await get_obj(model, session, id)

async def delete_object(model: Base, session: AsyncSession, id: int) -> Base:
    # Проверка на нахождения объекта по id
    obj = await get_obj(model, session, id)
    try:
        await session.delete(obj)
        await session.commit()
    except exc.IntegrityError:
        raise HTTPException(status_code=500, detail="This object has existing child objects. Deletion is not possible")

async def update_object_put(model: Base,
                            session: AsyncSession,
                            id: int,
                            data: dict,
                            fk_obj: dict = None,
                            update_fk: bool = False) -> Base:

    data.pop("id")
    obj = await get_obj(model, session, id)
    if update_fk:
        for k, v in fk_obj.items():
            setattr(obj, k, v)
    stmt = update(model).where(model.id == id).values(**data).execution_options(synchronize_session="fetch")
    await session.execute(stmt)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_fields_by_template(session: AsyncSession, template_id: int):
    query = select(TemplateField).where(TemplateField.template_id == template_id)
    result = await session.execute(query)
    objs = result.scalars().all()
    return objs





