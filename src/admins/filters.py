from typing import Union

from sqlalchemy.sql.selectable import Select

from admins.models import Topic
from database import Base
class BaseFilter:
    def get_not_null_filters(self, model: Base) -> list:
        filters_with_values = {k: v for k, v in self.__dict__.items() if v}
        filters = []
        for key, value in filters_with_values.items():
            filters.append(getattr(model, key) == value)
        return filters


class TopicFilter(BaseFilter):
    __model = Topic
    def __init__(self, name: str = None):
        self.name = name

    def has_categories(self, value: bool, query: Select) -> Union[Select, list]:
        if value:
            # noinspection PyTypeChecker
            return query.filter(self.__model.categories != None)
        return []

