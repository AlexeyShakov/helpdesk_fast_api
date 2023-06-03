import operator
from typing import Union, Optional, List

from sqlalchemy.sql.selectable import Select

from admins.models import Topic
from database import Base
from fields import Field
from sqlalchemy import select
from sqlalchemy import or_


class FilterExample:
    # сделать: может быть добавить параметр field_type(bool, str и тд) и сделать валидацию на входящие значения?
    name_filter = Field(filter_param="equal")
    has_categories_filter = Field(method="get_has_categories")
    operator_mapping = {
        "equal": operator.eq
    }


    class Meta:
        model = Topic

    def __init__(self, name: Optional[str] = None, has_categories: Optional[bool] = None):
        self.name = name
        self.has_categories = has_categories

    def process_filtering(self, fields: dict):
        custom_filters = []
        not_custom_queries = []
        for field, value in fields.items():
            needed_filter_field: Field = getattr(self, f"{field}_filter")
            if not needed_filter_field.method:
                # Собираем все дефолтные поля, чтобы разом отфильтровать кверисет
                custom_filters.append((field, value, self.operator_mapping[needed_filter_field.filter_param]))
            else:
                pass
                # if value is None:
                #     # Для параметров данного типа может быть три значения: True, False и None
                #     continue
                # else:
                #     needed_method = getattr(self, f"get_{field}")
                #     not_custom_queries.append(needed_method(value))
        default_filters_list = self.form_default_filters(custom_filters)
        # Получаем кверисет от дефолтных полей и потом мерджим к нему кастомные фильтры
        query = select(self.Meta.model).filter(or_(*default_filters_list))
        # сделать пока не работает, проверить работоспособность
        # if not_custom_queries:
        #     for not_custom_query in not_custom_queries:
        #         query = query.union(not_custom_query)
        return query

    def form_default_filters(self, fields_info: List[tuple]) -> list:
        # сделать: может быть для аргумента fields_info выбрать другой datatype, более точный? Мб класс или именованный кортеж?
        filters = []
        for field in fields_info:
            if field[1]:
                filters.append(operator.eq(getattr(self.Meta.model, field[0]), field[1]))
        return filters

    def get_has_categories(self, value: bool):
        if value:
            # noinspection PyTypeChecker
            return select(self.Meta.model).filter(self.Meta.model.categories != None)
        return []

