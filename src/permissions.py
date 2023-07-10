from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admins.models import Topic
from crud_handler import BaseHandler
from database import get_async_session
from staff.enums import UserRoleChoices
from staff.models import User


async def manage_helpdesk(request: Request, error_msg: str = None) -> None:
    user = request.user
    if not user.has_helpdesk_permission:
        raise HTTPException(status_code=403,
                            detail=error_msg or "You don't have permission to manage heldpesk")


async def access_ready_answers_list(request: Request, session: AsyncSession, error_msg: str = None) -> None:
    handler = BaseHandler(User)
    user_from_request = request.user
    user_from_db = await handler.get_obj(select(User), session, {"main_id": user_from_request.id})
    if not (user_from_request.has_helpdesk_permission or user_from_db.role):
        raise HTTPException(status_code=403,
                            detail=error_msg or "You don't have permission to get ready answers list")
