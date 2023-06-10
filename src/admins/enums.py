import enum

class TemplateFieldChoices(enum.Enum):
    SELECT = "select"
    STRING = "string"

class TypeChoices(str, enum.Enum):
    MIN = "M"
    HOUR = "H"
    DAY = "D"


class TopicOrderingChoices(str, enum.Enum):
    ASC_NAME = "name"
    ASC_ID = "id"
    DESC_NAME = "-name"
    DESC_ID = "-id"



class CategoryOrderingChoices(str, enum.Enum):
    ASC_NAME = "name"
    ASC_ID = "id"
    ASC_TOPIC = "topic"
    DESC_NAME = "-name"
    DESC_ID = "-id"
    DESC_TOPIC = "-topic"


class TemplateOrderingChoices(str, enum.Enum):
    ASC_NAME = "name"
    ASC_ID = "id"
    ASC_CATEGORY_COUNT = "category_count"
    DESC_NAME = "-name"
    DESC_ID = "-id"
    DESC_CATEGORY_COUNT = "-category_count"
