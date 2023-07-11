from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud_handler import BaseHandler
from staff.enums import UserRoleChoices
from staff.models import User


# +++++++++++
async def allow_create_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()
    handler = BaseHandler(User)

    needed_category = data["category"]
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})
    if user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == needed_category["id"]:
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "A user cannot create tickets in the category where he/she is specialist")


async def allow_read_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()

    handler = BaseHandler(User)
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})

    creator_or_supervisor = user_from_db.id == data["creator"]["id"] or (
            user_from_db.role == UserRoleChoices.SUPERVISOR and user_from_db.category.id == data["category"]["id"])

    if data["specialist"]:
        # If a specialist assigned to the ticket we have to check that a certain specialist can view it
        if not (user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.id == data["specialist"]["id"]) \
                or not creator_or_supervisor:
            raise HTTPException(status_code=403,
                                detail=error_msg or
                                       "The ticket can be viewed by the creator, specialist or supervisors of "
                                       "the category")

    else:
        if not creator_or_supervisor or not (
                user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == data["category"]["id"]):
            raise HTTPException(status_code=403,
                                detail=error_msg or
                                       "The ticket can be viewed only by the creator or by specialists or supervisors"
                                       "of the category where the ticket was created")


async def only_creator(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()

    handler = BaseHandler(User)
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})

    if user_from_db.id != data["creator"]["id"]:
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the creator of the ticket can make this action")


async def allow_take_and_reject_ticket(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()

    handler = BaseHandler(User)
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})

    if not (user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == data["category"]["id"]):
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the specialists from the ticket category can make this action")


async def allow_assign_specialist(request: Request, session: AsyncSession, error_msg: str = None):
    data = await request.json()

    handler = BaseHandler(User)
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})
    if not (user_from_db.role == UserRoleChoices.SUPERVISOR and user_from_db.category.id == data["category"]["id"]):
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the supervisors from the ticket category can make this action")
