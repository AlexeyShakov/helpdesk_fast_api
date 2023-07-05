from fastapi import HTTPException


def check_answers(data: dict) -> None:
    template_field = data.get("template_field")
    if template_field["required"] and (not data["value"] or not data["value"]["name"]):
        raise HTTPException(status_code=500, detail=f"This field \"{data['label']}\" is required")
