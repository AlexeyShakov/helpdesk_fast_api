from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admins.filters import ReadyAnswerFilter
from admins.models import ReadyAnswer, Category
from admins.schemas import ReadyAnswerSchemaCreate, ReadyAnswerSchemaReturn, SearchingSchema, ReadyAnswerFilterSchema
from crud_handler import BaseHandler
from database import get_async_session

ready_answers_router = InferringRouter(tags=["ReadyAnswer"])
ROUTE = "/api/ready_answers"


@cbv(ready_answers_router)
class TemplateView(BaseHandler):
    session: AsyncSession = Depends(get_async_session)

    def __init__(self):
        super().__init__(ReadyAnswer, ReadyAnswerFilter)

    @ready_answers_router.post(f"{ROUTE}/", response_model=ReadyAnswerSchemaReturn, status_code=201)
    async def create_ready_answer(self, ready_answer_object: ReadyAnswerSchemaCreate):
        ready_answer_dict = ready_answer_object.dict()
        obj = await self.get_obj(select(Category), self.session, ready_answer_dict.get("category").get("id"))
        ready_answer_dict["category"] = obj
        return await self.create(self.session, ready_answer_dict)

    @ready_answers_router.get(f"{ROUTE}/", response_model=List[ReadyAnswerSchemaReturn], status_code=200)
    async def read_ready_answers(self,
                                searching_params: SearchingSchema = Depends(SearchingSchema),
                                filter_params: ReadyAnswerFilterSchema = Depends(ReadyAnswerFilterSchema),
                                offset: int = 0,
                                limit: int = 5):
        search_fields = {
            "ordinary": {"column": "answer_text"},
            "related": []
        }
        query = select(self.model).join(Category)
        return await self.list(query=query,
                               filter_params=filter_params.dict(),
                               searching_params=searching_params.dict(),
                               search_fields=search_fields,
                               session=self.session,
                               limit=limit,
                               offset=offset)

    @ready_answers_router.delete(f"{ROUTE}/" + "{ready_answer_id}", status_code=204)
    async def delete_ready_answer(self, ready_answer_id: int):
        return await self.delete(self.session, ready_answer_id)

    @ready_answers_router.put(f"{ROUTE}/" + "{ready_answer_id}",
                              response_model=ReadyAnswerSchemaReturn,
                              status_code=200)
    async def update_template_field(self, ready_answer_id: int, ready_answer: ReadyAnswerSchemaReturn):
        ready_answer_dict = ready_answer.dict()
        category_data = ready_answer_dict.pop("category")
        fk_obj = {"category_id": category_data["id"]}
        return await self.update(
            session=self.session,
            id=ready_answer_id,
            data=ready_answer_dict,
            fk_obj=fk_obj,
            update_fk=True
        )
