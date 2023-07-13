from json import JSONDecodeError

from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud_handler import BaseHandler
from database import get_async_session
from staff.enums import UserRoleChoices
from staff.models import User
from tickets.models import Ticket


async def allow_ticket_management(request: Request, session: AsyncSession = Depends(get_async_session),
                                  error_msg: str = None):
    route = request["route"].name
    pk = request.path_params.get("ticket_id")
    try:
        data = await request.json()
    except JSONDecodeError:
        data = {}
    handler = BaseHandler(User)
    ticket = await handler.get_obj(select(Ticket), session, {"id": int(pk)}) if pk else None
    user_from_db = await handler.get_obj(select(User), session, {"main_id": request.user.id})
    permission_mapping = {
        "create_item": allow_create_ticket,
        "read_ticket": allow_read_ticket,
        "delete_ticket": only_creator,
        "update_ticket": only_creator,
        "take_ticket": allow_take_and_reject_ticket,
        "assign_specialist": allow_assign_specialist

    }
    if route == "read_tickets":
        return
    if permission_checker := permission_mapping.get(route):
        return await permission_checker(data, user_from_db, ticket)
    raise HTTPException(status_code=500,
                        detail=error_msg or "Unknown action")


async def allow_create_ticket(data: dict, user_from_db: User, ticket: Ticket, error_msg: str = None):
    if user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == data["category"]["id"]:
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "A user cannot create tickets in the category where he/she is specialist")


async def allow_read_ticket(data: dict, user_from_db: User, ticket: Ticket, error_msg: str = None):
    creator_or_supervisor = user_from_db.id == ticket.creator_id or (
            user_from_db.role == UserRoleChoices.SUPERVISOR and user_from_db.category.id == ticket.category_id
    )

    if ticket.specialist:
        # If a specialist assigned to the ticket we have to check that a certain specialist can view it
        if not (user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.id == ticket.specialist_id) \
                or not creator_or_supervisor:
            raise HTTPException(status_code=403,
                                detail=error_msg or
                                       "The ticket can be viewed by the creator, specialist or supervisors of "
                                       "the category")

    else:
        if not creator_or_supervisor or not (
                user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == ticket.category_id):
            raise HTTPException(status_code=403,
                                detail=error_msg or
                                       "The ticket can be viewed only by the creator or by specialists or supervisors"
                                       "of the category where the ticket was created")


async def only_creator(data: dict, user_from_db: User, ticket: Ticket, error_msg: str = None):
    if user_from_db.id != ticket.creator_id:
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the creator of the ticket can make this action")


async def allow_take_and_reject_ticket(data: dict, user_from_db: User, ticket: Ticket, error_msg: str = None):
    if not (user_from_db.role == UserRoleChoices.SPECIALIST and user_from_db.category.id == ticket.category_id):
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the specialists from the ticket category can make this action")


async def allow_assign_specialist(data: dict, user_from_db: User, ticket: Ticket, error_msg: str = None):
    if not (user_from_db.role == UserRoleChoices.SUPERVISOR and user_from_db.category.id == ticket.category_id):
        raise HTTPException(status_code=403,
                            detail=error_msg or
                                   "Only the supervisors from the ticket category can make this action")
