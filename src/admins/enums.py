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
