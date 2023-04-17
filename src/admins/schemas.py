from pydantic import BaseModel
from .models import Section

class SectionSchemaCreate(BaseModel):
    name: str

class SectionSchemaReturn(SectionSchemaCreate):
    id: int
    class Config:
        orm_mode = True

class TopicCreate(BaseModel):
    name: str
    section: SectionSchemaReturn

class TopicReturn(TopicCreate):
    id: int

    class Config:
        orm_mode = True





