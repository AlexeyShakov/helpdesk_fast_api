import enum


class TicketStatusChoice(enum.Enum):
    NEW = "new"
    WAITING_SPEC = "waiting_for_a_specialist"
    WAITING_CLIENT = "waiting_for_a_client"
    CLOSED = "closed"
    REJECTED = "rejected"


class GradeChoice(enum.Enum):
    BAD = 1
    NORMAL = 2
    GOOD = 3
