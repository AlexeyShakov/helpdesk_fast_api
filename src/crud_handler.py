from fastapi import HTTPException
from typing import Sequence, Optional
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy import select, update, exc, or_
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError

from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from filters import BaseFilter
from sqlalchemy.sql.selectable import Select


class BaseHandler:
    ordering_mapper = {
        "asc": asc,
        "desc": desc
    }
    filter_class = None

    def __init__(self, model: Base, filter_class: Optional[BaseFilter] = None):
        self.model = model
        self.filter_class = filter_class

    async def create(self, session: AsyncSession, data: dict) -> Base:
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def list(self,
                   offset: int,
                   limit: int,
                   session: AsyncSession,
                   joined_ordering: Optional[dict] = None,
                   ordering_params: Optional[dict] = None,
                   filter_params: Optional[dict] = None,
                   search_fields: Optional[dict] = None,
                   searching_params: Optional[dict] = None
                   ) -> Sequence:
        # Для взаимодействия со связанными объектами
        if joined_ordering:
            query = select(self.model).join(
                joined_ordering["related_table"], getattr(self.model, joined_ordering["related_field_name"])
            )
        else:
            query = select(self.model)
        # Pagination
        query = query.offset(offset * limit).limit(limit)
        # Filtering
        if self.filter_class and filter_params and any([v for k, v in filter_params.items()]):
            print("Я тут", filter_params)
            print("filter_class", self.filter_class)
            filter_instance = self.filter_class(**filter_params)
            print("filter_instance", filter_instance)
            print("asda", filter_instance.__dict__)
            query = filter_instance.process_filtering(filter_instance.__dict__, query)
        ###
        # Sorting
        if ordering_params and (ordering_field := ordering_params.get("ordering")):
            query = await self.order_query(query, ordering_field, joined_ordering)
        # Searching
        if searching_params and searching_params["search"]:
            query = await self.make_search(searching_params, search_fields, query)

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
        try:
            await session.execute(stmt)
        except IntegrityError:
            raise HTTPException(status_code=500,
                                detail=f"There is no object with id={v} for {k}")
        await session.commit()
        await session.refresh(obj)
        return obj

    async def order_query(self, query, ordering_field: str, joined_ordering: Optional[dict]):
        ordering = self.ordering_mapper["desc"] if ordering_field[0] == "-" else self.ordering_mapper["asc"]
        field_name = ordering_field[1:] if ordering_field[0] == "-" else ordering_field
        if joined_ordering:
            query = query.order_by(
                ordering(
                    getattr(joined_ordering["related_table"], joined_ordering["ordering_field"])
                )
            )
        else:
            query = query.order_by(ordering(field_name))
        return query

    async def make_search(self, searching_params: dict, search_fields: dict, query: Select):
        ordinary_search = [
            getattr(self.model, value).
            like(f"%{searching_params['search']}%") for key, value in search_fields["ordinary"].items()
        ]
        related_search = [
            getattr(element["table"], element["column"]).
            like(f"%{searching_params['search']}%") for element in search_fields["related"]
        ]
        return query.filter(or_
                            (*related_search, *ordinary_search)
                            )
