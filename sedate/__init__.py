""" Methods that deal with dates and timezones.

There are projects like `Arrow <https://github.com/crsmithdev/arrow>`_ or
`Delorean <https://github.com/crsmithdev/arrow>`_ which provide ways to work
with timezones without having to think about it too much.

Libres doesn't use them because its author *wants* to think about these things,
to ensure they are correct, and partly because of self-loathing.

Adding another layer makes these things harder.

That being said, further up the stacks - in the web application for example -
it might very well make sense to use a datetime wrapper library.

"""

import operator
import pytz

from calendar import weekday, monthrange
from datetime import datetime, time, timedelta


from typing import overload
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from datetime import date as Date

    from .types import DateLike
    from .types import DateOrDatetime
    from .types import Direction
    from .types import TDateOrDatetime
    from .types import TzInfoOrName

__version__ = '0.3.0'

mindatetime = pytz.utc.localize(datetime.min)
maxdatetime = pytz.utc.localize(datetime.max)


class NotTimezoneAware(Exception):
    pass


def ensure_timezone(timezone: 'TzInfoOrName') -> pytz.BaseTzInfo:
    """ Make sure the given timezone is a pytz timezone, not just a string. """

    if isinstance(timezone, str):
        return pytz.timezone(timezone)

    return timezone


def as_datetime(value: 'DateLike') -> datetime:
    """ Turns a date-ish object into a datetime object. """
    if isinstance(value, datetime):
        return value

    return datetime(value.year, value.month, value.day)


def standardize_date(date: datetime, timezone: 'TzInfoOrName') -> datetime:
    """ Takes the given date and converts it to UTC.

    The given timezone is set on timezone-naive dates and converted to
    on timezone-aware dates. That essentially means that you should pass
    the timezone that you know the date to be, even if the date is in another
    timezone (like UTC) or if the date does not have a timezone set.

    """

    if not timezone:
        raise ValueError('The timezone may *not* be empty!')

    if date.tzinfo is None:
        date = replace_timezone(date, timezone)

    return to_timezone(date, 'UTC')


def replace_timezone(date: datetime, timezone: 'TzInfoOrName') -> datetime:
    """ Takes the given date and replaces the timezone with the given timezone.

    No conversion is done in this method, it's simply a safe way to do the
    following (which is problematic with timzones that have daylight saving
    times)::

        # don't do this:
        date.replace(tzinfo=timezone('Europe/Zurich'))

        # do this:
        calendar.replace_timezone(date, 'Europe/Zurich')

    """

    timezone = ensure_timezone(timezone)

    return timezone.normalize(timezone.localize(date.replace(tzinfo=None)))


def to_timezone(date: datetime, timezone: 'TzInfoOrName') -> datetime:
    """ Takes the given date and converts it to the given timezone.

    The given date must already be timezone aware for this to work.

    """

    if not date.tzinfo:
        raise NotTimezoneAware()

    timezone = ensure_timezone(timezone)
    return timezone.normalize(date.astimezone(timezone))


def utcnow() -> datetime:
    """ Returns a timezone-aware datetime.utcnow(). """
    return replace_timezone(datetime.utcnow(), 'UTC')


def is_whole_day(
    start: datetime,
    end: datetime,
    timezone: 'TzInfoOrName'
) -> bool:
    """Returns true if the given start, end range should be considered
    a whole-day range. This is so if the start time is 0:00:00 and the end
    time either 0:59:59 or 0:00:00 and if there is at least a diff
    erence of 23h 59m 59s / 86399 seconds between them.

    """

    # without replacing the tzinfo, the total seconds count later will return
    # the wrong number - it is correct, because the total seconds do not
    # constitute a whole day, but we are not interested in the actual time
    # but we need to know that the day starts at 0:00 and ends at 24:00,
    # between which we need 24 hours (just looking at the time)
    start = to_timezone(start, timezone).replace(tzinfo=None)
    end = to_timezone(end, timezone).replace(tzinfo=None)

    if start > end:
        raise ValueError('The end needs to be equal or greater than the start')

    if (start.hour, start.minute, start.second) != (0, 0, 0):
        return False

    if (end.hour, end.minute, end.second) not in ((0, 0, 0), (23, 59, 59)):
        return False

    if (end - start).total_seconds() < 86399:
        return False

    return True


@overload
def overlaps(start: datetime, end: datetime,
             otherstart: datetime, otherend: datetime) -> bool: ...
@overload  # noqa: E302
def overlaps(start: 'Date', end: 'Date',
             otherstart: 'Date', otherend: 'Date') -> bool: ...


def overlaps(
    start: 'DateOrDatetime',
    end: 'DateOrDatetime',
    otherstart: 'DateOrDatetime',
    otherend: 'DateOrDatetime'
) -> bool:
    """ Returns True if the given dates overlap in any way. """

    if otherstart <= start and start <= otherend:
        return True

    if start <= otherstart and otherstart <= end:
        return True

    return False


@overload
def count_overlaps(dates: Iterable[Tuple[datetime, datetime]],
                   start: datetime, end: datetime) -> int: ...
@overload  # noqa: E302
def count_overlaps(dates: Iterable[Tuple['Date', 'Date']],
                   start: 'Date', end: 'Date') -> int: ...


def count_overlaps(
    dates: Iterable[Tuple['DateOrDatetime', 'DateOrDatetime']],
    start: 'DateOrDatetime',
    end: 'DateOrDatetime'
) -> int:
    """ Goes through the list of start/end tuples in 'dates' and returns the
    number of times start/end overlaps with any of the dates.

    """
    count = 0

    for otherstart, otherend in dates:
        count += overlaps(start, end, otherstart, otherend) and 1 or 0

    return count


def align_date_to_day(
    date: datetime,
    timezone: 'TzInfoOrName',
    direction: 'Direction'
) -> datetime:
    """ Aligns the given date to the beginning or end of the day, depending on
    the direction. The beginning of the day only makes sense with a timezone
    (as it is a local thing), so the given timezone is used.

    The date however is always returned in the timezone it already is in.
    The time will be adjusted instead

    E.g.
    2012-1-24 10:00 down -> 2012-1-24 00:00
    2012-1-24 10:00 up   -> 2012-1-24 23:59:59'999999

    """
    assert direction in ('up', 'down')

    aligned = (0, 0, 0, 0) if direction == 'down' else (23, 59, 59, 999999)

    local = to_timezone(date, timezone)

    if (local.hour, local.minute, local.second, local.microsecond) == aligned:
        return date

    adjusted = local.replace(hour=0, minute=0, second=0, microsecond=0)

    if direction == 'up':
        adjusted = adjusted + timedelta(days=1, microseconds=-1)

    # we want the date in the timezone it ends up in. Say we switch to
    # summertime at 02:00 and we want a date set at 03:00 to be adjusted
    # downwards. In this case we want the result to end up in the timezone
    # before the change to summertime (since at 00:00 it was not yet in effect)
    tz = ensure_timezone(timezone)
    normalized = tz.normalize(adjusted)
    assert isinstance(normalized.tzinfo, pytz.BaseTzInfo)
    adjusted = replace_timezone(adjusted, normalized.tzinfo)

    # FIXME: Allow other tzinfo implementations?
    assert isinstance(date.tzinfo, pytz.BaseTzInfo)
    return to_timezone(adjusted, date.tzinfo)


def align_range_to_day(
    start: datetime,
    end: datetime, timezone: 'TzInfoOrName'
) -> Tuple[datetime, datetime]:
    """ Takes the given start and end date and aligns it to the day depending
    on the given timezone.

    """
    assert start <= end, "{} - {} is an invalid range".format(start, end)

    return (
        align_date_to_day(start, timezone, 'down'),
        align_date_to_day(end, timezone, 'up')
    )


def align_date_to_week(
    date: datetime,
    timezone: 'TzInfoOrName',
    direction: 'Direction'
) -> datetime:
    """ Like :func:`align_date_to_day`, but for weeks.

    The first day of the week is monday.

    """
    date = align_date_to_day(date, timezone, direction)

    if direction == 'down':
        return date - timedelta(
            days=weekday(date.year, date.month, date.day))
    else:
        return date + timedelta(
            days=6 - weekday(date.year, date.month, date.day))


def align_range_to_week(
    start: datetime,
    end: datetime,
    timezone: 'TzInfoOrName'
) -> Tuple[datetime, datetime]:

    if start > end:
        raise ValueError(f'{start} - {end} is an invalid range')

    return (
        align_date_to_week(start, timezone, 'down'),
        align_date_to_week(end, timezone, 'up')
    )


def align_date_to_month(
    date: datetime,
    timezone: 'TzInfoOrName',
    direction: 'Direction'
) -> datetime:
    """ Like :func:`align_date_to_day`, but for months. """
    date = align_date_to_day(date, timezone, direction)

    if direction == 'down':
        return date.replace(day=1)
    else:
        return date.replace(day=monthrange(date.year, date.month)[1])


def align_range_to_month(
    start: datetime,
    end: datetime,
    timezone: 'TzInfoOrName'
) -> Tuple[datetime, datetime]:

    if start > end:
        raise ValueError(f'{start} - {end} is an invalid range')

    return (
        align_date_to_month(start, timezone, 'down'),
        align_date_to_month(end, timezone, 'up')
    )


def get_date_range(
    day: datetime,
    start_time: time,
    end_time: time
) -> Tuple[datetime, datetime]:
    """ Returns the date-range of a date a start and an end time. """

    start = datetime.combine(day.date(), start_time).replace(tzinfo=day.tzinfo)
    end = datetime.combine(day.date(), end_time).replace(tzinfo=day.tzinfo)

    # since the user can only one date with separate times it is assumed
    # that an end before a start is meant for the following day
    if end < start:
        end += timedelta(days=1)

    return start, end


def parse_time(timestring: str) -> time:
    """ Parses the given string in 'HH:MM' format and returns a time instance.

    """

    hour, minute = (int(p) for p in timestring.split(':'))

    if hour == 24:
        hour = 0

    return time(hour, minute)


def dtrange(
    start: 'TDateOrDatetime',
    end: 'TDateOrDatetime',
    step: timedelta = timedelta(days=1)
) -> Iterator['TDateOrDatetime']:
    """ Yields dates between start and end (inclusive) using the given step
    size. The step size may be negative iff end < start.

    The type of start/end is kept (datetime => datetime, date => date).

    """

    if start <= end:
        remaining = operator.le
    else:
        remaining = operator.ge

        if step.total_seconds() > 0:
            step = timedelta(seconds=step.total_seconds() * -1)

    while remaining(start, end):
        yield start

        # dates are immutable, so no copy is needed
        start += step


def weeknumber(day: 'DateOrDatetime') -> int:
    """ The weeknumber of the given date/dateime as defined by ISO 8601. """
    # FIXME: This is super inefficient
    return int(day.strftime('%V'))


def weekrange(
    start: 'TDateOrDatetime',
    end: 'TDateOrDatetime'
) -> Iterator[Tuple['TDateOrDatetime', 'TDateOrDatetime']]:
    """ Yields the weeks between start and end (inclusive).

    If start and end span less than a week, a single start/end pair is the
    result.

    if start and end span multiple weeks a start/end pair for each week is
    returned (start being monday, end being sunday).

    Like :func:`dtrange` this function works with both datetime and date.
    Unlike :func:`dtrange` this function does not work backwards (start > end).

    """

    if start > end:
        # TODO: We can probably make this work backwards as well...
        raise ValueError(f'{start} - {end} is an invalid range')

    s = e = start
    last_week = weeknumber(start)

    # FIXME: doing a step of 1 day is really dumb and makes us do
    #        much more work than we need to
    for day in dtrange(start, end):
        if last_week != weeknumber(day):
            yield s, e
            s = e = day
            last_week = weeknumber(s)
        else:
            e = day

    yield s, e
