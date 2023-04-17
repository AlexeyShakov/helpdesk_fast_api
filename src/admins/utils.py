from fastapi import HTTPException
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_obj(model: Base, session: AsyncSession, id: int):
    query = select(model).where(model.id == id)
    result = await session.execute(query)
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj