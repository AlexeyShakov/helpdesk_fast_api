from admins.utils import get_obj
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from sqlalchemy import update, exc
from fastapi import  HTTPException

async def create(model: Base, session: AsyncSession, data: dict) -> Base:
    obj = model(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def get_list(model: Base, session: AsyncSession, offset: int, limit: int) -> Sequence:
    query = select(model).offset(offset).limit(limit)
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
    """

    :param model:
    :param session:
    :param id:
    :param data:
    :param fk_obj: Объекты, связанные с обновяемым объектом связью foreign key
    :param update_fk:
    :return:
    """
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





