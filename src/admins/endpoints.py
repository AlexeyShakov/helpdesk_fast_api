from fastapi import APIRouter, Depends
from .schemas import SectionSchemaCreate, SectionSchemaReturn, SectionOptional, SectionSchemaKek
from .crud import create, get_list, get_object, delete_object, update_object_put
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Section
from typing import List

from database import get_async_session


router = APIRouter(
    prefix="/sections",
    tags=["Section"]
)

@router.post("/", response_model=SectionSchemaReturn, status_code=201)
async def create_section(section_object: SectionSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    return await create(Section, session, section_object.dict())
@router.get("/", response_model=List[SectionSchemaReturn], status_code=200)
async def read_sections(session: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 2):
    return await get_list(Section, session, offset, limit)

@router.get("/{section_id}", response_model=SectionSchemaReturn, status_code=200)
async def read_section(section_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_object(Section, session, section_id)
@router.delete("/{section_id}", status_code=204)
async def delete_section(section_id: int, session: AsyncSession = Depends(get_async_session)):
    return await delete_object(Section, session, section_id)

@router.put("/{section_id}", status_code=200, response_model=SectionSchemaReturn)
async def update_put_section(section_id: int, section: SectionSchemaReturn, session: AsyncSession = Depends(get_async_session)):
    return await update_object_put(Section, session, section_id, section.dict())

@router.patch("/{section_id}", status_code=200, response_model=SectionSchemaKek)
async def update_patch_section(section_id: int, section: SectionOptional, session: AsyncSession = Depends(get_async_session)):
    print("Я тут")
    print("data",  section.dict(exclude_unset=True))
    return await update_object_put(Section, session, section_id, section.dict(exclude_unset=True))
