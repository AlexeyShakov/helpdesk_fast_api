from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud_handler import BaseHandler
from staff.enums import UserRoleChoices
from staff.models import User


async def allow_create_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()
    handler = BaseHandler(User)

    print("data", data)
    needed_category = data["category"]
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})
    if user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == needed_category["id"]:
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "A user cannot create tickets in the category where he/she is specialist")


async def allow_read_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    pass


async def only_creator(request: Request, session: AsyncSession, error_msg: str = None):
    pass


async def allow_take_and_reject_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    pass


async def allow_assign_specialist(request: Request, session: AsyncSession, error_msg: str = None):
    pass
