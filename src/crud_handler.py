from fastapi import HTTPException
from typing import Sequence, Optional
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy import select, update, exc
from sqlalchemy import desc, asc
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession


class BaseHandler:
    ordering_mapper = {
        "asc": asc,
        "desc": desc
    }
    def __init__(self, model: Base):
        self.model = model

    async def create(self, session: AsyncSession, data: dict) -> Base:
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def list(self,
                   session: AsyncSession,
                   joined_ordering: Optional[dict] = None,
                   ordering_params: Optional[dict] = None,
                   ) -> Sequence:
        if joined_ordering:
            query = select(self.model).join(
                joined_ordering["related_table"], getattr(self.model, joined_ordering["related_field_name"])
            )
        else:
            query = select(self.model)
        if ordering_params and (ordering_field := ordering_params.get("ordering")):
            query = await self.order_query(query, ordering_field, joined_ordering)
        result = await session.execute(query)
        if type(result) == CursorResult:
            needed_objects = result.all()
        else:
            needed_objects = result.scalars().all()
        return needed_objects

    async def retrieve(self, session: AsyncSession, obj_id: int) -> Base:
        return await self.get_obj(self.model, session, obj_id)

    async def delete(self, session: AsyncSession, obj_id: int) -> Base:
        obj = await self.get_obj(self.model, session, obj_id)
        try:
            await session.delete(obj)
            await session.commit()
        except exc.IntegrityError:
            raise HTTPException(status_code=500,
                                detail="This object has existing child objects. Deletion is not possible")

    async def get_obj(self, model: Base, session: AsyncSession, obj_id: int) -> Base:
        query = select(model).filter_by(id=obj_id)
        result = await session.execute(query)
        obj = result.scalars().first()
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj

    async def update(
            self,
            session: AsyncSession,
            id: int,
            data: dict,
            fk_obj: dict = None,
            update_fk: bool = False
    ):
        data.pop("id")
        obj = await self.get_obj(self.model, session, id)
        if update_fk:
            for k, v in fk_obj.items():
                setattr(obj, k, v)
        stmt = update(self.model).filter_by(id=id).values(**data).execution_options(synchronize_session="fetch")
        await session.execute(stmt)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def order_query(self, query, ordering_field: str, joined_ordering: Optional[dict]):
        ordering = self.ordering_mapper["desc"] if ordering_field[0] == "-" else self.ordering_mapper["asc"]
        field_name = ordering_field[1:]
        if joined_ordering:
            query = query.order_by(
                ordering(
                    getattr(joined_ordering["related_table"], joined_ordering["ordering_field"])
                )
            )
        else:
            query = query.order_by(ordering(field_name))
        return query
