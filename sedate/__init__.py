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

from calendar import monthrange
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
    from .types import TzInfo
    from .types import TzInfoOrName

__version__ = '1.0.2'

mindatetime = pytz.utc.localize(datetime.min)
maxdatetime = pytz.utc.localize(datetime.max)


class NotTimezoneAware(Exception):
    pass


def ensure_timezone(timezone: 'TzInfoOrName') -> 'TzInfo':
    """ Make sure the given timezone is a pytz timezone, not just a string. """

    if isinstance(timezone, str):
        return pytz.timezone(timezone)

    # NOTE: We make our lives slightly easier by accepting BaseTzInfo
    #       but returning the more specific classes, since the function
    #       signatures for normalize/localize differ from the base class
    return timezone  # type:ignore[return-value]


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

    return to_timezone(date, pytz.UTC)


def replace_timezone(
    date: datetime,
    timezone: 'TzInfoOrName',
    *,
    is_dst: bool = False,
    raise_non_existent: bool = False,
    raise_ambiguous: bool = False,
) -> datetime:
    """ Takes the given date and replaces the timezone with the given timezone.

    No conversion is done in this method, it's simply a safe way to do the
    following (which is problematic with timzones that have daylight saving
    times)::

        # don't do this:
        date.replace(tzinfo=timezone('Europe/Zurich'))

        # do this:
        sedate.replace_timezone(date, 'Europe/Zurich')

    By default this will pick standard time for ambiguous times but just
    as with DstTzInfo.normalize you can use `is_dst` to either pick the
    other.

    If you want to detect ambiguous/missing datetimes in the given timezone
    you may optionally raise `pytz.NonExistentTimeError` or
    `pytz.AmbiguousTimeError`

    """

    timezone = ensure_timezone(timezone)
    naive = date.replace(tzinfo=None)
    may_raise = raise_non_existent or raise_ambiguous
    try:
        localized = timezone.localize(
            naive,
            is_dst=None if may_raise else is_dst
        )
    except pytz.NonExistentTimeError as error:
        if raise_non_existent:
            raise error

        localized = timezone.localize(naive, is_dst=is_dst)
    except pytz.AmbiguousTimeError as error:
        if raise_ambiguous:
            raise error
        localized = timezone.localize(naive, is_dst=is_dst)

    return timezone.normalize(localized)


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
    return replace_timezone(datetime.utcnow(), pytz.UTC)


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

    tzinfo = ensure_timezone(timezone)
    local = to_timezone(date, tzinfo)

    if (local.hour, local.minute, local.second, local.microsecond) == aligned:
        return date

    adjusted = local.replace(hour=0, minute=0, second=0, microsecond=0)

    if direction == 'up':
        adjusted = adjusted + timedelta(days=1, microseconds=-1)

    # we want the date in the timezone it ends up in. Say we switch to
    # summertime at 02:00 and we want a date set at 03:00 to be adjusted
    # downwards. In this case we want the result to end up in the timezone
    # before the change to summertime (since at 00:00 it was not yet in effect)
    normalized = tzinfo.normalize(adjusted)
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
    if start > end:
        raise ValueError(f'{start} - {end} is an invalid range')

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

    # we need the localized time to determine the weekday
    # but we need to align to day at the end to avoid DST
    # <-> ST transition issues the same we do in align_to_day
    localized = to_timezone(date, timezone)
    if direction == 'down':
        return align_date_to_day(
            date - timedelta(days=localized.weekday()),
            timezone,
            'down'
        )
    else:
        return align_date_to_day(
            date + timedelta(days=6 - localized.weekday()),
            timezone,
            direction
        )


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

    # FIXME: This is really inefficient, but we're forced to do
    #        this due to the weird/poor API design of decoupling
    #        the timezone from the date, which may seem convenient
    #        in some situations, but it also means we do a dozen
    #        redundant conversions back and forth if we want to
    #        implement functions in terms of one another
    tzinfo = date.tzinfo
    assert isinstance(tzinfo, pytz.BaseTzInfo)
    localized = to_timezone(date, timezone)
    date = align_date_to_day(date, timezone, direction)

    # we need to align to day at the end to handle DST <-> ST
    # transitions properly
    if direction == 'down':
        return align_date_to_day(
            to_timezone(localized.replace(day=1), tzinfo),
            timezone,
            'down'
        )
    else:
        last_day = localized.replace(day=monthrange(date.year, date.month)[1])
        return align_date_to_day(
            to_timezone(last_day, tzinfo),
            timezone,
            direction
        )


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


def offset_date(
    date: 'TDateOrDatetime',
    delta: timedelta,
    *,
    is_dst: bool = False,
    raise_non_existent: bool = False,
    raise_ambiguous: bool = False
) -> 'TDateOrDatetime':
    """ For date and most datetimes it will be the same as adding the
    the date and delta naively, but for datetimes with a DstTzInfo it
    will make sure a DST <-> ST transition won't shift the time by an
    hour backwards or forwards.

    Refer to :func:`replace_timezone` for behaviour of `is_dst`
    """
    if not isinstance(date, datetime):
        return date + delta

    if not isinstance(date.tzinfo, pytz.tzinfo.DstTzInfo):
        return date + delta

    tzinfo = date.tzinfo
    naive_end = date.replace(tzinfo=None) + delta
    return replace_timezone(
        naive_end,
        tzinfo,
        is_dst=is_dst,
        raise_non_existent=raise_non_existent,
        raise_ambiguous=raise_ambiguous
    )


def get_date_range(
    day: datetime,
    start_time: time,
    end_time: time,
    *,
    is_dst: bool = False,
    raise_non_existent: bool = False,
    raise_ambiguous: bool = False
) -> Tuple[datetime, datetime]:
    """ Returns the date-range of a date, a start and an end time.

    For timezones with daylight savings this might return a range
    that goes backwards on a ST -> DST transition::

    2.30 -> 3.00 will result in 2.30 ST -> 3.00 DST

    which is the same as 3.30 DST -> 3.00 DST

    If you wish to properly handle this case and ambiguous times
    then you will need to use `raise_non_existent=True` in order
    to be able to respond to `pytz.AmbiguousTimeError`.

    """

    date = day.date()
    tzinfo = day.tzinfo

    start = datetime.combine(date, start_time)
    end = datetime.combine(date, end_time)

    if isinstance(tzinfo, pytz.tzinfo.DstTzInfo):
        # we need to be more careful about DST <-> ST transitions
        start = replace_timezone(
            start,
            tzinfo,
            is_dst=is_dst,
            raise_ambiguous=raise_ambiguous,
            raise_non_existent=raise_non_existent
        )
        end = replace_timezone(
            end,
            tzinfo,
            is_dst=is_dst,
            raise_ambiguous=raise_ambiguous,
            raise_non_existent=raise_non_existent
        )
    else:
        # in this case we can just replace it back in
        start = start.replace(tzinfo=tzinfo)
        end = end.replace(tzinfo=tzinfo)

    # since the user can only one date with separate times it is assumed
    # that an end before a start is meant for the following day
    if end < start:
        end = offset_date(
            end,
            timedelta(days=1),
            is_dst=is_dst,
            raise_non_existent=raise_non_existent,
            raise_ambiguous=raise_ambiguous
        )

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
    end: 'DateOrDatetime',
    step: timedelta = timedelta(days=1),
    *,
    skip_missing: bool = False
) -> Iterator['TDateOrDatetime']:
    """ Yields dates between start and end (inclusive) using the given step
    size. The step size may be negative iff end < start.

    The type of start/end is kept (datetime => datetime, date => date).


    The below only applies to timezones with daylight savings::

    For ambiguous time periods the overlapping DST hour will be skipped.

    For non-existent time periods we snap to the previous hour, so the same
    hour will potentially be returned twice (once in ST and once in DST).
    You can instead skip the missing hour by passing `skip_missing=True`

    """

    # TODO: We might want to be able to optionally include the duplicate
    #       hour on DST -> ST transition days. But that will get really
    #       messy for steps smaller than an hour, if we want to preserve
    #       the absolute order of the datetimes. It would probably be
    #       easier/smarter to use dateutil at that point
    tzinfo = None
    if isinstance(start, datetime):
        if isinstance(start.tzinfo, pytz.tzinfo.DstTzInfo):
            # we want the underspecified version that doesn't know yet
            # whether
            tzinfo = start.tzinfo

            # we convert to a tz-naive datetimes
            start = start.replace(tzinfo=None)
            if isinstance(end, datetime):
                # before we convert the end to naive we need to make
                # sure they're not in completely different timezones
                assert isinstance(end.tzinfo, pytz.BaseTzInfo)
                if end.tzinfo.zone != tzinfo.zone:
                    end = to_timezone(end, tzinfo)

                end = end.replace(tzinfo=None)

    if start <= end:
        remaining = operator.le
    else:
        remaining = operator.ge

        if step.total_seconds() > 0:
            step = timedelta(seconds=step.total_seconds() * -1)

    def date_iter() -> Iterator['TDateOrDatetime']:
        # dates are immutable, so no copy is needed
        current = start
        while remaining(current, end):
            yield current
            current += step

    if not tzinfo:
        # we don't need to convert values back to the source timezone
        yield from date_iter()
        return

    # back-convert each element to original timezone
    for date in date_iter():
        assert isinstance(date, datetime)
        try:
            yield replace_timezone(
                date, tzinfo, raise_non_existent=skip_missing
            )
        except pytz.NonExistentTimeError:
            pass


def weeknumber(date: 'DateOrDatetime') -> int:
    return date.isocalendar()[1]


def weekrange(
    start: 'TDateOrDatetime',
    end: 'TDateOrDatetime'
) -> Iterator[Tuple['TDateOrDatetime', 'TDateOrDatetime']]:
    """ Yields the weeks between start and end (inclusive).

    If start and end span less than a week, a single start/end pair is the
    result.

    if start and end span multiple weeks a start/end pair for each week is
    returned (start being monday, end being sunday).

    Like :func:`dtrange` this function works with both datetime and date
    and works backwards. In the backwards case the start/end pairs will be
    backwards as well.

    """

    # we start by aligning the start to the end of the 1st week
    # we then iterate over the end dates of the week
    if start <= end:
        day_step = timedelta(days=1)
        week_step = timedelta(days=7)
        aligned_start = start + timedelta(days=6 - start.weekday())
    else:
        # here the start and end are backwards
        day_step = timedelta(days=-1)
        week_step = timedelta(days=-7)
        aligned_start = start - timedelta(days=start.weekday())

    s = start
    for e in dtrange(aligned_start, end, week_step):
        yield s, e
        s = offset_date(e, day_step)

    # in the rare case that the end is perfectly aligned we will
    # already have yielded it, so only yield it if we need to
    if e != end:
        yield s, end
