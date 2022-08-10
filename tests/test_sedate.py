import pytest
import sedate
import pytz

from datetime import date, datetime, time, timedelta


UTC = pytz.timezone('UTC')
CETCEST = pytz.timezone('Europe/Zurich')


def test_ensure_timezone():
    assert sedate.ensure_timezone('Europe/Zurich') \
        == pytz.timezone('Europe/Zurich')

    assert sedate.ensure_timezone(pytz.timezone('Europe/Zurich')) \
        == pytz.timezone('Europe/Zurich')


def test_utcnow():

    assert sedate.utcnow().replace(
        tzinfo=None, microsecond=0, second=0, minute=0) \
        == datetime.utcnow().replace(microsecond=0, second=0, minute=0)

    assert sedate.utcnow().tzinfo == UTC


def test_as_datetime():

    class Dateish(object):
        year = 2014
        month = 8
        day = 11

    as_datetime = sedate.as_datetime

    assert as_datetime(Dateish()) == datetime(2014, 8, 11)
    assert as_datetime(date(2015, 1, 1)) == datetime(2015, 1, 1)
    assert as_datetime(datetime(2015, 1, 1, 10)) == datetime(2015, 1, 1, 10)


def test_replace_timezone_amibiguous():
    with pytest.raises(pytz.AmbiguousTimeError):
        sedate.replace_timezone(
            datetime(2022, 10, 30, 2),
            'Europe/Zurich',
            raise_ambiguous=True
        )


def test_replace_timezone_non_existent():
    with pytest.raises(pytz.NonExistentTimeError):
        sedate.replace_timezone(
            datetime(2022, 3, 27, 2),
            'Europe/Zurich',
            raise_non_existent=True
        )


def test_standardize_naive_date():
    naive_date = datetime(2014, 10, 1, 13, 30)
    normalized = sedate.standardize_date(naive_date, 'Europe/Zurich')

    assert normalized.tzname() == 'UTC'
    assert normalized.replace(tzinfo=None) == datetime(2014, 10, 1, 11, 30)


def test_standardize_aware_date():
    aware_date = sedate.replace_timezone(
        datetime(2014, 10, 1, 13, 30), 'Europe/Zurich')

    normalized = sedate.standardize_date(aware_date, 'Europe/Zurich')

    assert normalized.tzname() == 'UTC'
    assert normalized.replace(tzinfo=None) == datetime(2014, 10, 1, 11, 30)


def test_standardize_missing_timezone():
    naive_date = datetime(2014, 10, 1, 13, 30)

    with pytest.raises(ValueError, match=r'may \*not\* be empty'):
        sedate.standardize_date(naive_date, None)

    with pytest.raises(ValueError, match=r'may \*not\* be empty'):
        sedate.standardize_date(naive_date, '')


def test_is_whole_day():
    assert sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 7, 1), 'Europe/Zurich'),
        'Europe/Zurich'
    )

    assert sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 59), 'Europe/Zurich'),
        'Europe/Zurich'
    )

    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 1), 'Europe/Zurich'),
        'Europe/Zurich'
    )
    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 58), 'Europe/Zurich'),
        'Europe/Zurich'
    )
    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30, 0, 0, 0, 999), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 59), 'Europe/Zurich'),
        'Europe/Zurich'
    )


def test_is_whole_day_end_before_start():
    with pytest.raises(ValueError, match=r'end needs to be equal'):
        sedate.is_whole_day(
            sedate.replace_timezone(
                datetime(2015, 6, 30, 23, 59, 59), 'Europe/Zurich'),
            sedate.replace_timezone(
                datetime(2015, 6, 30), 'Europe/Zurich'),
            'Europe/Zurich'
        )


def test_count_overlaps():
    assert sedate.count_overlaps([
        (datetime(2015, 1, 1, 10, 0), datetime(2015, 1, 1, 11, 0)),
        (datetime(2015, 1, 1, 12, 0), datetime(2015, 1, 1, 13, 0))
    ], datetime(2015, 1, 1, 10), datetime(2015, 1, 10, 13)) == 2


def test_align_range_to_day():
    assert sedate.align_range_to_day(
        start=sedate.replace_timezone(
            datetime(2015, 1, 1, 10, 0), 'Europe/Zurich'),
        end=sedate.replace_timezone(
            datetime(2015, 1, 1, 11, 0), 'Europe/Zurich'),
        timezone='Europe/Zurich'
    ) == (
        sedate.replace_timezone(
            datetime(2015, 1, 1), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 1, 1, 23, 59, 59, 999999), 'Europe/Zurich')
    )


def test_get_date_range():
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2015, 1, 1), 'Europe/Zurich'),
        time(12, 0),
        time(11, 0),
    ) == (
        sedate.replace_timezone(datetime(2015, 1, 1, 12), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2015, 1, 2, 11), 'Europe/Zurich'),
    )
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2015, 1, 1), 'Europe/Zurich'),
        time(12, 30),
        time(14, 0),
    ) == (
        sedate.replace_timezone(datetime(2015, 1, 1, 12, 30), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2015, 1, 1, 14, 0), 'Europe/Zurich'),
    )


def test_get_date_range_dst_to_st_transition():
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2022, 10, 30), 'Europe/Zurich'),
        time(2, 0),
        time(3, 0),
    ) == (
        sedate.replace_timezone(datetime(2022, 10, 30, 2), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 30, 3), 'Europe/Zurich'),
    )
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2022, 10, 29), 'Europe/Zurich'),
        time(12, 0),
        time(11, 0),
    ) == (
        sedate.replace_timezone(datetime(2022, 10, 29, 12), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 30, 11), 'Europe/Zurich'),
    )
    with pytest.raises(pytz.AmbiguousTimeError):
        sedate.get_date_range(
            sedate.replace_timezone(datetime(2022, 10, 30), 'Europe/Zurich'),
            time(2, 0),
            time(3, 0),
            raise_ambiguous=True
        )


def test_get_date_range_st_to_dst_transition():
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2022, 3, 27), 'Europe/Zurich'),
        time(1, 0),
        time(2, 0),
    ) == (
        sedate.replace_timezone(datetime(2022, 3, 27, 1), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 2), 'Europe/Zurich'),
    )
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2022, 3, 26), 'Europe/Zurich'),
        time(12, 0),
        time(11, 0),
    ) == (
        sedate.replace_timezone(datetime(2022, 3, 26, 12), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 11), 'Europe/Zurich'),
    )
    with pytest.raises(pytz.NonExistentTimeError):
        sedate.get_date_range(
            sedate.replace_timezone(datetime(2022, 3, 27), 'Europe/Zurich'),
            time(1, 0),
            time(2, 0),
            raise_non_existent=True
        )


def test_is_whole_day_summertime():

    start = sedate.standardize_date(
        datetime(2014, 10, 26, 0, 0, 0), 'Europe/Zurich')

    end = sedate.standardize_date(
        datetime(2014, 10, 26, 23, 59, 59), 'Europe/Zurich')

    assert sedate.is_whole_day(start, end, 'Europe/Zurich')
    assert not sedate.is_whole_day(start, end, 'Europe/Istanbul')


def test_is_whole_day_wintertime():

    start = sedate.standardize_date(
        datetime(2015, 3, 29, 0, 0, 0), 'Europe/Zurich')

    end = sedate.standardize_date(
        datetime(2015, 3, 29, 23, 59, 59), 'Europe/Zurich')

    assert sedate.is_whole_day(start, end, 'Europe/Zurich')
    assert not sedate.is_whole_day(start, end, 'Europe/Istanbul')


def test_require_timezone_awareness():

    naive = datetime(2014, 10, 26, 0, 0, 0)

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.to_timezone(naive, 'UTC')

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.is_whole_day(naive, naive, 'UTC')

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.align_date_to_day(naive, 'UTC', 'up')


def test_overlaps():

    overlaps = [
        [
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ],
        [
            datetime(2013, 1, 1, 11, 0), datetime(2013, 1, 1, 12, 0),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ]
    ]

    doesnt = [
        [
            datetime(2013, 1, 1, 11, 0), datetime(2013, 1, 1, 11, 59, 59),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ]
    ]

    tz = 'Europe/Zurich'

    for dates in overlaps:
        assert sedate.overlaps(*dates)

        timezone_aware = [sedate.standardize_date(d, tz) for d in dates]
        assert sedate.overlaps(*timezone_aware)

    for dates in doesnt:
        assert not sedate.overlaps(*dates)

        timezone_aware = [sedate.standardize_date(d, tz) for d in dates]
        assert not sedate.overlaps(*timezone_aware)


def test_align_date_to_day_down():

    unaligned = sedate.standardize_date(datetime(2012, 1, 24, 10), 'UTC')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.tzname() == 'UTC'
    assert aligned == sedate.standardize_date(
        datetime(2012, 1, 24, 0), 'Europe/Zurich')

    already_aligned = sedate.replace_timezone(
        datetime(2012, 1, 1), 'Europe/Zurich'
    )

    assert already_aligned == sedate.align_date_to_day(
        already_aligned, 'Europe/Zurich', 'down')


def test_align_date_to_day_summertime():

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-03-26T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-03-26T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-27T21:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-27T21:59:59.999999+00:00'


def test_align_date_to_day_wintertime():

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-10-29T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-10-29T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-30T22:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-30T22:59:59.999999+00:00'


def test_align_date_to_day_up():
    unaligned = sedate.standardize_date(datetime(2012, 1, 24, 10), 'UTC')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.tzname() == 'UTC'
    assert aligned == sedate.standardize_date(
        datetime(2012, 1, 24, 23, 59, 59, 999999), 'Europe/Zurich')

    already_aligned = sedate.replace_timezone(
        datetime(2012, 1, 1, 23, 59, 59, 999999), 'Europe/Zurich'
    )

    assert already_aligned == sedate.align_date_to_day(
        already_aligned, 'Europe/Zurich', 'up')


def test_parse_time():
    assert sedate.parse_time('00:00') == time(0, 0)
    assert sedate.parse_time('24:00') == time(0, 0)
    assert sedate.parse_time('23:59') == time(23, 59)

    with pytest.raises(ValueError):
        sedate.parse_time('99:99')


@pytest.mark.parametrize('date', [
    datetime(2016, 3, 28, 15, tzinfo=UTC),
    datetime(2016, 3, 29, 15, tzinfo=UTC),
    datetime(2016, 3, 30, 15, tzinfo=UTC),
    datetime(2016, 3, 31, 15, tzinfo=UTC),
    datetime(2016, 4, 1, 15, tzinfo=UTC),
    datetime(2016, 4, 2, 15, tzinfo=UTC),
    datetime(2016, 4, 3, 15, tzinfo=UTC)
])
def test_align_date_to_week(date):

    assert sedate.align_date_to_week(date, 'UTC', 'down')\
        == datetime(2016, 3, 28, tzinfo=UTC)

    assert sedate.align_date_to_week(date, 'UTC', 'up')\
        == datetime(2016, 4, 3, 23, 59, 59, 999999, tzinfo=UTC)


def test_align_range_to_week():
    full_week = (
        datetime(2016, 3, 28, tzinfo=UTC),
        datetime(2016, 4, 3, 23, 59, 59, 999999, tzinfo=UTC)
    )
    assert sedate.align_range_to_week(
        datetime(2016, 3, 28, 15, tzinfo=UTC),
        datetime(2016, 4, 3, 15, tzinfo=UTC),
        timezone='UTC'
    ) == full_week
    assert sedate.align_range_to_week(
        datetime(2016, 3, 30, 15, tzinfo=UTC),
        datetime(2016, 3, 30, 15, tzinfo=UTC),
        timezone='UTC'
    ) == full_week


def test_align_range_to_week_invalid_range():
    with pytest.raises(ValueError, match=r'invalid range'):
        sedate.align_range_to_week(
            datetime(2016, 3, 30, 16, tzinfo=UTC),
            datetime(2016, 3, 30, 15, tzinfo=UTC),
            timezone='UTC'
        )
    with pytest.raises(ValueError, match=r'invalid range'):
        sedate.align_range_to_week(
            datetime(2016, 4, 3, 15, tzinfo=UTC),
            datetime(2016, 3, 30, 15, tzinfo=UTC),
            timezone='UTC'
        )


def test_align_date_to_week_st_to_dst():

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-03-20T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-03-20T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-27T21:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-27T21:59:59.999999+00:00'


def test_align_date_to_week_dst_to_st():

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-10-23T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-10-23T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-30T22:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_week(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-30T22:59:59.999999+00:00'


@pytest.mark.parametrize('date', [
    datetime(2012, 2, day, 15, tzinfo=UTC)
    for day in range(1, 30)
])
def test_align_date_to_month(date):

    assert sedate.align_date_to_month(date, 'UTC', 'down')\
        == datetime(2012, 2, 1, tzinfo=UTC)

    assert sedate.align_date_to_month(date, 'UTC', 'up')\
        == datetime(2012, 2, 29, 23, 59, 59, 999999, tzinfo=UTC)


def test_align_date_to_month_st_to_dst():

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-02-29T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-02-29T23:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-31T21:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 3, 27, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-03-31T21:59:59.999999+00:00'


def test_align_date_to_month_dst_to_st():

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-09-30T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'down')

    assert aligned.isoformat() == '2016-09-30T22:00:00+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 1), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-31T22:59:59.999999+00:00'

    unaligned = sedate.standardize_date(
        datetime(2016, 10, 30, 4), 'Europe/Zurich')
    aligned = sedate.align_date_to_month(unaligned, 'Europe/Zurich', 'up')

    assert aligned.isoformat() == '2016-10-31T22:59:59.999999+00:00'


def test_align_range_to_month():
    full_month = (
        datetime(2012, 2, 1, tzinfo=UTC),
        datetime(2012, 2, 29, 23, 59, 59, 999999, tzinfo=UTC)
    )
    assert sedate.align_range_to_month(
        datetime(2012, 2, 1, 15, tzinfo=UTC),
        datetime(2012, 2, 29, 15, tzinfo=UTC),
        timezone='UTC'
    ) == full_month
    assert sedate.align_range_to_month(
        datetime(2012, 2, 15, 15, tzinfo=UTC),
        datetime(2012, 2, 15, 15, tzinfo=UTC),
        timezone='UTC'
    ) == full_month


def test_align_range_to_month_invalid_range():
    with pytest.raises(ValueError, match=r'invalid range'):
        sedate.align_range_to_month(
            datetime(2012, 2, 15, 16, tzinfo=UTC),
            datetime(2012, 2, 15, 15, tzinfo=UTC),
            timezone='UTC'
        )
    with pytest.raises(ValueError, match=r'invalid range'):
        sedate.align_range_to_month(
            datetime(2012, 2, 29, 15, tzinfo=UTC),
            datetime(2012, 2, 1, 15, tzinfo=UTC),
            timezone='UTC'
        )


def test_dtrange():

    def dtrange(*args):
        return tuple(sedate.dtrange(*args))

    assert dtrange(datetime(2017, 1, 1), datetime(2017, 1, 1)) == (
        datetime(2017, 1, 1),
    )

    assert dtrange(datetime(2017, 1, 1), datetime(2017, 1, 2)) == (
        datetime(2017, 1, 1),
        datetime(2017, 1, 2),
    )

    assert dtrange(date(2017, 1, 1), date(2017, 1, 2)) == (
        date(2017, 1, 1),
        date(2017, 1, 2),
    )

    assert dtrange(
        datetime(2017, 1, 1, 10), datetime(2017, 1, 1, 12), timedelta(hours=1)
    ) == (
        datetime(2017, 1, 1, 10),
        datetime(2017, 1, 1, 11),
        datetime(2017, 1, 1, 12),
    )

    assert dtrange(date(2017, 1, 5), date(2017, 1, 1)) == (
        date(2017, 1, 5),
        date(2017, 1, 4),
        date(2017, 1, 3),
        date(2017, 1, 2),
        date(2017, 1, 1),
    )

    assert dtrange(date(2017, 1, 5), date(2017, 1, 1), timedelta(days=2)) == (
        date(2017, 1, 5),
        date(2017, 1, 3),
        date(2017, 1, 1),
    )

    assert dtrange(date(2017, 1, 5), date(2017, 1, 1), timedelta(days=-2)) == (
        date(2017, 1, 5),
        date(2017, 1, 3),
        date(2017, 1, 1),
    )


def test_dtrange_tz_aware_dst_to_st():

    def dtrange(*args):
        return tuple(sedate.dtrange(*args))

    assert dtrange(
        sedate.replace_timezone(datetime(2022, 10, 30), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 31), 'Europe/Zurich')
    ) == (
        sedate.replace_timezone(datetime(2022, 10, 30), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 31), 'Europe/Zurich')
    )

    assert dtrange(
        sedate.replace_timezone(datetime(2022, 10, 30, 2), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 30, 4), 'Europe/Zurich'),
        timedelta(hours=1)
    ) == (
        sedate.replace_timezone(datetime(2022, 10, 30, 2), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 30, 3), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 10, 30, 4), 'Europe/Zurich'),
    )


def test_dtrange_tz_aware_st_to_dst():

    def dtrange(*args, skip_missing=False):
        return tuple(sedate.dtrange(*args, skip_missing=skip_missing))

    assert dtrange(
        sedate.replace_timezone(datetime(2022, 3, 27), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 28), 'Europe/Zurich')
    ) == (
        sedate.replace_timezone(datetime(2022, 3, 27), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 28), 'Europe/Zurich')
    )

    assert dtrange(
        sedate.replace_timezone(datetime(2022, 3, 27, 1), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 3), 'Europe/Zurich'),
        timedelta(hours=1)
    ) == (
        # 2:00 and 3:00 are the same time on this day since 2:00-2:59 will
        # be returned in ST, while 3:00 onwards will be returned in DST
        sedate.replace_timezone(datetime(2022, 3, 27, 1), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 2), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 3), 'Europe/Zurich'),
    )

    assert dtrange(
        sedate.replace_timezone(datetime(2022, 3, 27, 1), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 3), 'Europe/Zurich'),
        timedelta(hours=1),
        skip_missing=True
    ) == (
        sedate.replace_timezone(datetime(2022, 3, 27, 1), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 27, 3), 'Europe/Zurich'),
    )


def test_weekrange():

    def weekrange(*args):
        return tuple(sedate.weekrange(*args))

    assert weekrange(date(2017, 1, 1), date(2017, 1, 8)) == (
        (date(2017, 1, 1), date(2017, 1, 1)),
        (date(2017, 1, 2), date(2017, 1, 8))
    )

    assert weekrange(date(2017, 1, 2), date(2017, 1, 8)) == (
        (date(2017, 1, 2), date(2017, 1, 8)),
    )

    assert weekrange(datetime(2017, 1, 1), datetime(2017, 1, 1)) == (
        (datetime(2017, 1, 1), datetime(2017, 1, 1)),
    )

    assert weekrange(datetime(2017, 1, 12), datetime(2017, 1, 5)) == (
        (datetime(2017, 1, 12), datetime(2017, 1, 9)),
        (datetime(2017, 1, 8), datetime(2017, 1, 5)),
    )


@pytest.mark.parametrize('interval', [
    (date(2017, 1, 1), date(2017, 1, 8)),
])
def test_weekrange_backward(interval):
    forward = tuple(sedate.weekrange(*interval))
    backward = tuple(sedate.weekrange(*reversed(interval)))

    # reversing should not change the number of results
    assert len(forward) == len(backward)

    # all the intervals should come in in opposite order
    # and each interval should be reversed
    for f, b in zip(forward, reversed(backward)):
        assert f == tuple(reversed(b))


def test_weekrange_tz_aware_dst_to_st():

    def weekrange(*args):
        return tuple(sedate.weekrange(*args))

    def tz_aware_range(start, end):
        return (
            sedate.replace_timezone(start, 'Europe/Zurich'),
            sedate.replace_timezone(end, 'Europe/Zurich')
        )

    assert weekrange(
        sedate.replace_timezone(datetime(2022, 3, 22), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 28), 'Europe/Zurich')
    ) == (
        tz_aware_range(datetime(2022, 3, 22), datetime(2022, 3, 27)),
        tz_aware_range(datetime(2022, 3, 28), datetime(2022, 3, 28)),
    )

    assert weekrange(
        sedate.replace_timezone(datetime(2022, 3, 22, 3), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2022, 3, 28, 3), 'Europe/Zurich')
    ) == (
        tz_aware_range(datetime(2022, 3, 22, 3), datetime(2022, 3, 27, 3)),
        tz_aware_range(datetime(2022, 3, 28, 3), datetime(2022, 3, 28, 3)),
    )


def test_weeknumber():
    assert sedate.weeknumber(date(2022, 8, 10)) == 32
    assert sedate.weeknumber(datetime(2022, 8, 10)) == 32
