from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence
from sqlalchemy import update

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
    # Проверка на нахождения объекта по id
    query = select(model).filter(model.id == id)
    result = await session.execute(query)
    return result.scalars().first()

async def delete_object(model: Base, session: AsyncSession, id: int) -> Base:
    # Проверка на нахождения объекта по id
    obj = await session.get(model, id)
    await session.delete(obj)
    await session.commit()

async def update_object_put(model: Base, session: AsyncSession, id: int, data: dict) -> Base:
    #Проверка на нахождения объекта по id
    stmt = update(model).where(model.id == id).values(**data).execution_options(synchronize_session="fetch")
    await session.execute(stmt)
    await session.commit()
    return await session.get(model, id)






