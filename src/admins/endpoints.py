from fastapi import APIRouter, Depends
from .schemas import SectionSchemaCreate, SectionSchemaReturn
from sqlalchemy.ext.asyncio import AsyncSession
from admins.models import Section

from database import get_async_session


router = APIRouter(
    prefix="/sections",
    tags=["Section"]
)

@router.post("/", response_model=SectionSchemaReturn, status_code=201)
async def create_section(section_object: SectionSchemaCreate, session: AsyncSession = Depends(get_async_session)):
    # Создать отдельный файл для crud операций и перенести туда эту логику
    section = Section(**section_object.dict())
    session.add(section)
    await session.commit()
    await session.refresh(section)
    return section

