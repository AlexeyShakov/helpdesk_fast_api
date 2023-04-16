from pydantic import BaseModel
from typing import Optional


class SectionSchemaCreate(BaseModel):
    # Как сделать поле необязательным???
    name: str

class SectionSchemaReturn(SectionSchemaCreate):
    id: int
    class Config:
        orm_mode = True



