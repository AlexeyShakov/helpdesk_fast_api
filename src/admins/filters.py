from typing import Optional
from sqlalchemy.sql.selectable import Exists
from admins.models import Topic, Template
from fields import Field
from filters import BaseFilter


class TopicFilter(BaseFilter):
    name_filter = Field(filter_param="equal")
    has_categories_filter = Field(method="get_has_categories")

    class Meta:
        model = Topic

    def __init__(self, name: Optional[str] = None, has_categories: Optional[bool] = None):
        self.name = name
        self.has_categories = has_categories

    def get_has_categories(self, value: bool) -> Optional[Exists]:
        if value:
            return self.Meta.model.categories != None
        return None


class TemplateFilter(BaseFilter):
    has_fields_filter = Field(method="get_has_fields")

    class Meta:
        model = Template

    def __init__(self, has_fields: Optional[bool] = None):
        self.has_fields = has_fields

    def get_has_fields(self, value: bool) -> Optional[Exists]:
        if value:
            return self.Meta.model.template_fields != None
        return None
