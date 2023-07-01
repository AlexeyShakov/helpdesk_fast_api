from pydantic import BaseModel


class GroupSchemaCreate(BaseModel):
    name: str


class GroupSchemaReturn(GroupSchemaCreate):
    id: int

    class Config:
        orm_mode = True
