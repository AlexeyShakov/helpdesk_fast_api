from pydantic import BaseModel

from staff.enums import UserRoleChoices


class GroupSchemaCreate(BaseModel):
    name: str


class GroupSchemaReturn(GroupSchemaCreate):
    id: int

    class Config:
        orm_mode = True


class UserSchemaCreate(BaseModel):
    username: str
    last_name: str
    first_name: str
    surname: str
    phone: str
    email: str
    group: GroupSchemaReturn
    main_id: int
    role: UserRoleChoices


class UserSchemaReturn(UserSchemaCreate):
    id: int

    class Config:
        orm_mode = True