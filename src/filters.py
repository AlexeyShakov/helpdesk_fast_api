import operator
from sqlalchemy.sql.selectable import Select
from typing import List
from sqlalchemy import or_

from fields import Field


class BaseFilter:
    operator_mapping = {
        "equal": operator.eq
    }

    class Meta:
        model = None

    def process_filtering(self, fields: dict, query: Select) -> Select:
        custom_filters = []
        not_custom_filters = []
        for field, value in fields.items():
            needed_filter_field: Field = getattr(self, f"{field}_filter")
            if not needed_filter_field.method:
                # Собираем все дефолтные поля, чтобы разом отфильтровать кверисет
                custom_filters.append((field, value, self.operator_mapping[needed_filter_field.filter_param]))
            else:
                if value is None:
                    # Для параметров данного типа может быть три значения: True, False и None
                    continue
                else:
                    needed_method = getattr(self, f"get_{field}")
                    not_custom_filters.append(needed_method(value))
        needed_filters = []
        needed_filters.extend(self.form_default_filters(custom_filters))
        needed_filters.extend(not_custom_filters)
        return query.filter(or_(*needed_filters))

    def form_default_filters(self, fields_info: List[tuple]) -> list:
        filters = []
        for field in fields_info:
            if field[1]:
                filters.append(field[2](getattr(self.Meta.model, field[0]), field[1]))
        return filters