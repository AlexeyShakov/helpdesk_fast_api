import re
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from admins.schemas import CategoryOnlyIDSchema
from staff.enums import UserRoleChoices


class GroupSchemaCreate(BaseModel):
    name: str


class GroupSchemaReturn(GroupSchemaCreate):
    id: int

    class Config:
        orm_mode = True

class UserSchemaPrivateInfo(BaseModel):
    phone: str
    email: EmailStr

class UserSchemaBase(BaseModel):
    username: str
    last_name: str
    first_name: str
    surname: str
    group: Optional[GroupSchemaReturn]
    main_id: int
    role: Optional[UserRoleChoices]
    category: Optional[CategoryOnlyIDSchema]


class UserSchemaCreate(UserSchemaBase, UserSchemaPrivateInfo):
    @validator("phone")
    def validate_phone(cls, field_value: str):
        reg = re.compile(r"^\+\d{5,20}$")
        if not re.match(reg, field_value):
            raise ValueError("The phone number is not valid")
        return field_value

class UserSchemaReturn(UserSchemaBase):
    id: int

    class Config:
        orm_mode = True
