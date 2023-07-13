from fastapi import Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud_handler import BaseHandler
from database import get_async_session
from staff.models import User


async def allow_helpdesk_management(request: Request, session: AsyncSession = Depends(get_async_session),
                                    error_msg: str = None):
    route = request["route"].name
    user = request.user
    if route == "read_ready_answers":
        await access_ready_answers_list(user, session)
    else:
        await manage_helpdesk(user)


async def manage_helpdesk(user: User, error_msg: str = None) -> None:
    if not user.has_helpdesk_permission:
        raise HTTPException(status_code=403,
                            detail=error_msg or "You don't have permission to manage heldpesk")


async def access_ready_answers_list(user_from_request: User, session: AsyncSession, error_msg: str = None) -> None:
    handler = BaseHandler(User)
    user_from_db = await handler.get_obj(select(User), session, {"main_id": user_from_request.id})
    if not (user_from_request.has_helpdesk_permission or user_from_db.role):
        raise HTTPException(status_code=403,
                            detail=error_msg or "You don't have permission to get ready answers list")
