from abc import ABC
from datetime import datetime


class CssOrder(ABC):
    items: list
    name: str
    service: str
    ordered_at: datetime
