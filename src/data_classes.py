from typing import Callable


class DefaultFilterParam:
    def __init__(self, field_name: str, value: str, operation: Callable):
        """
        An instance of build-in operators like "operator.eq" and others
        """
        self.field_name = field_name
        self.value = value
        self.operation = operation
