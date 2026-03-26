from __future__ import annotations

import datetime
import pytz

from typing import Literal
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar


class HasDateAttrs(Protocol):
    year: int
    month: int
    day: int


AmbiguousAction: TypeAlias = Literal['skip_dst', 'skip_st', 'include_both']
DateOrDatetime: TypeAlias = datetime.date | datetime.datetime
DateLike: TypeAlias = DateOrDatetime | HasDateAttrs
DateOrDatetimeT = TypeVar('DateOrDatetimeT', datetime.date, datetime.datetime)
Direction: TypeAlias = Literal['up', 'down']
TzInfo: TypeAlias = (
    pytz._UTCclass | pytz.tzinfo.StaticTzInfo | pytz.tzinfo.DstTzInfo
)
TzInfoOrName: TypeAlias = pytz.BaseTzInfo | str
