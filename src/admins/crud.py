from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence


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
    query = select(model).filter(model.id == id)
    result = await session.execute(query)
    return result.scalars().first()

async def delete_object(model: Base, session: AsyncSession, id: int) -> Base:
    obj = await session.get(model, id)
    await session.delete(obj)
    await session.commit()



