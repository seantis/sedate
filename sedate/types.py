import datetime
import pytz

from typing import Literal
from typing import Protocol
from typing import TypeVar
from typing import Union


class HasDateAttrs(Protocol):
    year: int
    month: int
    day: int


DateOrDatetime = Union[datetime.date, datetime.datetime]
DateLike = Union[DateOrDatetime, HasDateAttrs]
TDateOrDatetime = TypeVar('TDateOrDatetime', datetime.date, datetime.datetime)
Direction = Literal['up', 'down']
TzInfoOrName = Union[pytz.BaseTzInfo, str]
