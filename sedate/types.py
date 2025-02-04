from __future__ import annotations

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


AmbiguousAction = Literal['skip_dst', 'skip_st', 'include_both']
DateOrDatetime = Union[datetime.date, datetime.datetime]
DateLike = Union[DateOrDatetime, HasDateAttrs]
DateOrDatetimeT = TypeVar('DateOrDatetimeT', datetime.date, datetime.datetime)
Direction = Literal['up', 'down']
TzInfo = Union[pytz._UTCclass, pytz.tzinfo.StaticTzInfo, pytz.tzinfo.DstTzInfo]
TzInfoOrName = Union[pytz.BaseTzInfo, str]
