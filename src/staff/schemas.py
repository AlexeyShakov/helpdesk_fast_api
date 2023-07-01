import re

from pydantic import BaseModel, EmailStr, validator

from admins.schemas import CategoryOnlyIDSchema
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
    email: EmailStr
    group: GroupSchemaReturn
    main_id: int
    role: UserRoleChoices
    category: CategoryOnlyIDSchema

    @validator("phone")
    def validate_phone(cls, field_value: str):
        reg = re.compile(r"^\+\d{5,20}$")
        if not re.match(reg, field_value):
            raise ValueError("The phone number is not valid")

class UserSchemaReturn(UserSchemaCreate):
    id: int

    class Config:
        orm_mode = True
