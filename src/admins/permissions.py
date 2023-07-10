from fastapi import Request, HTTPException


def manage_helpdesk(request: Request, error_msg: str = None) -> None:
    user = request.user
    if not user.has_helpdesk_permission:
        raise HTTPException(status_code=403,
                            detail=error_msg or "You don't have permission to manage heldpesk")
