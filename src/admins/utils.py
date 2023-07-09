from fastapi import HTTPException

from admins.enums import TemplateFieldChoices
from admins.models import TemplateField
from admins.schemas import SelectDataSchema, NameSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic.error_wrappers import ValidationError
from pydantic import BaseModel


async def validate_template_field_answer_value(template_field: TemplateField, value: dict, label: str) -> None:
    if template_field.type == TemplateFieldChoices.SELECT:
        if template_field.required and not value:
            raise HTTPException(status_code=400, detail={f"value": "This field is required"})
        await validate_by_pydantic_schema(SelectDataSchema, value)
    elif template_field.type == TemplateFieldChoices.STRING:
        await validate_by_pydantic_schema(NameSchema, value)
        if template_field.required and value["name"] == "":
            raise HTTPException(status_code=400, detail={f"value": "This field is required"})


async def validate_by_pydantic_schema(schema: BaseModel, value: dict) -> None:
    try:
        schema(**value)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception:
        raise HTTPException(status_code=400, detail={"uknown_error": "uknown error when validating"})


async def get_fields_by_template(session: AsyncSession, template_id: int):
    query = select(TemplateField).where(TemplateField.template_id == template_id)
    result = await session.execute(query)
    objs = result.scalars().all()
    return objs
