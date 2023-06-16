import operator
from sqlalchemy.sql.selectable import Select
from typing import List, Callable
from sqlalchemy import or_

from data_classes import DefaultFilterParam
from fields import Field


class BaseFilter:
    operator_mapping = {
        "equal": operator.eq
    }

    class Meta:
        model = None

    def process_filtering(self, fields: dict, query: Select) -> Select:
        """
        There are two types of filters. The first one is related with model fields and these fields are filtered by such
        operators as equal, greater and so on. You can find these operators in the "operator_mapping" attribute.
        These filters are so called "default_filters". The names of such filters(in children classes) have to follow
        this pattern <{some name}_filter>.

        The second type of filters are more complex and the result of them might be based on other fields, for example.
        The filters of this type are called "custom_filters". The names of such filters(in children classes) have to
        follow this pattern <get_{some name}>
        """
        dafault_filters = []
        custom_filters = []
        for field, value in fields.items():
            # The name of filter fields in children classes have to follow this pattern <some_name_filter>
            needed_filter_field: Field = getattr(self, f"{field}_filter")
            if not needed_filter_field.method:
                # Gather all default fields to filter queryset by all filters at once
                dafault_filters.append(
                    DefaultFilterParam(field, value, self.operator_mapping[needed_filter_field.filter_param])
                )
            else:
                if value is None:
                    # Three possible values: None, False and True
                    continue
                else:
                    # The names of filter fields for custom filters in children classes have to follow this pattern <some_name_filter>
                    needed_method = getattr(self, f"get_{field}")
                    custom_filters.append(needed_method(value))
        needed_filters = []
        needed_filters.extend(self.form_default_filters(dafault_filters))
        needed_filters.extend(custom_filters)
        return query.filter(or_(*needed_filters))

    def form_default_filters(self, fields_info: List[DefaultFilterParam]) -> list:
        """
        fields_info: [(field name, value for filtering, function for filtering like eq, gt and so on)]
        """
        filters = []
        for field in fields_info:
            if field.value:
                filters.append(field.operation(getattr(self.Meta.model, field.field_name), field.value))
        return filters
