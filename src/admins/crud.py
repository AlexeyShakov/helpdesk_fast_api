from admins.models import TemplateField
from admins.utils import get_obj
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from sqlalchemy import update, exc
from fastapi import HTTPException
from sqlalchemy.engine.cursor import CursorResult
from admins import filters
from sqlalchemy import desc


async def create(model: Base, session: AsyncSession, data: dict) -> Base:
    obj = model(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_list(model: Base,
                   session: AsyncSession,
                   filter_class_name: Optional[str] = None,
                   filter_params: Optional[dict] = None,
                   ordering_params: Optional[dict] = None,
                   joined_ordering: Optional[dict] = None,
                   offset: int = 0,
                   limit: int = 2,
                   ) -> Sequence:
    if ordering_params is None:
        ordering_params = dict()
    if filter_params is None:
        filter_params = dict()
    if joined_ordering is None:
        filter_params = dict()
    query = select(model)
    if filter_class_name and any([v for k, v in filter_params.items()]):
        filter_class = getattr(filters, filter_class_name)
        filter_instance = filter_class(**filter_params)
        query = filter_instance.process_filtering(filter_instance.__dict__, query)
    if ordering_field := ordering_params.get("ordering"):
        if joined_ordering:
            query = query.join(
                joined_ordering["related_table"], getattr(model, joined_ordering["related_field_name"])
            ) \
                .order_by(desc(getattr(joined_ordering["related_table"], joined_ordering["ordering_field"])))
        else:
            query = query.order_by(desc(ordering_field))
    # query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    if type(result) == CursorResult:
        needed_objects = result.all()
    else:
        needed_objects = result.scalars().all()
    return needed_objects


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

