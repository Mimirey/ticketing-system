import enum
class TicketType(str, enum.Enum):
    BUG ="Bug"
    FEATURE_REQUEST= "Feature Request"
class TicketPriority(str, enum.Enum):
    LOW="Low"
    MEDIUM="Medium"
    HIGH="High"
    CRITICAL="Critical"
class TicketStatus(str, enum.Enum):
    OPEN="Open"
    ASSIGNED="Assigned"
    IN_PROGRESS="In Progress"
    QA="QA"
    DONE="Done"