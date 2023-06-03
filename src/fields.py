class Field:
    def __init__(self, filter_param: str = None, method: str = None):
        if filter_param and method or not any((filter_param, method)):
            # сделать: а как эти внутренние ошибки будут отдаваться на фронт? И будут ли?
            raise ValueError("You have to enter either filter_param or method")
        if filter_param:
            self.filter_param = filter_param
            self.method = None
        else:
            self.filter_param = None
            self.method = method
