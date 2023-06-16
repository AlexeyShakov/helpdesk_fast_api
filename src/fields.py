from fastapi import HTTPException


class Field:
    """
    This class describes the parameters of filters. There are two types of filters - default and customs.
    If a filter is default we need to indicate just "filter_param". It says to us which operator we have to use for
    filtering like "equal", "greater", "less" or etc.

    For custom filters we have to point which method will handle filtering.
    """
    def __init__(self, filter_param: str = None, method: str = None):
        if filter_param and method or not any((filter_param, method)):
            raise HTTPException(status_code=500, detail="Inner error with filters. You have to enter either filter_param or method")
        if filter_param:
            self.filter_param = filter_param
            self.method = None
        else:
            self.filter_param = None
            self.method = method
