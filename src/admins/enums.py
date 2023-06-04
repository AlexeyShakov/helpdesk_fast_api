import enum

class TemplateFieldChoices(enum.Enum):
    SELECT = "select"
    STRING = "string"

class TypeChoices(str, enum.Enum):
    MIN = "M"
    HOUR = "H"
    DAY = "D"


class TopicOrderingChoices(str, enum.Enum):
    NAME = "name"
    ID = "id"


class CategoryOrderingChoices(str, enum.Enum):
    NAME = "name"
    ID = "id"
    TOPIC = "topic"


class TemplateOrderingChoices(str, enum.Enum):
    NAME = "name"
    ID = "id"
    CATEGORY_COUNT = "category_count"
