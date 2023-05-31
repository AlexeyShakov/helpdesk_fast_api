class TopicFilter:
    def __init__(self, name: str = None, id: int = None):
        self.name = name
        self.id = id

    def get_list_for_filters(self):
        return {k: v for k, v in self.__dict__.items() if v}
