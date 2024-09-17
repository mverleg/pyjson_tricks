#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests timezone-aware date/time objects, which need pytz. Naive date/times should
work with just Python code functionality, and are tested in `nonp`.
"""

from datetime import datetime, date, time, timedelta, timezone
from ro_json import dumps, loads
from ro_json.utils import is_py3
import pytz


DTOBJ = [
    datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7),
	datetime.now(timezone.utc),
    pytz.UTC.localize(datetime(year=1988, month=3, day=15, minute=3, second=59, microsecond=7)),
    pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, microsecond=7)),
    date(year=1988, month=3, day=15),
    time(hour=8, minute=3, second=59, microsecond=123),
    time(hour=8, second=59, microsecond=123, tzinfo=pytz.timezone('Europe/Amsterdam')),
	time(hour=8, second=59, microsecond=123, tzinfo=timezone.utc),
    timedelta(days=2, seconds=3599),
    timedelta(days=0, seconds=-42, microseconds=123),
    [{'obj': [pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, microsecond=7))]}],
]


def test_tzaware_date_time_without_dst():
    json = dumps(DTOBJ)
    back = loads(json)
    assert DTOBJ == back
    for orig, bck in zip(DTOBJ, back):
        assert orig == bck
        assert type(orig) == type(bck)
    txt = '{"__datetime__": null, "year": 1988, "month": 3, "day": 15, "hour": 8, "minute": 3, ' \
          '"second": 59, "microsecond": 7, "tzinfo": "Europe/Amsterdam"}'
    obj = loads(txt)
    assert obj == pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7))


def test_tzaware_date_time_with_dst():
    json = dumps(DTOBJ)
    back = loads(json)
    assert DTOBJ == back
    for orig, bck in zip(DTOBJ, back):
        assert orig == bck
        assert type(orig) == type(bck)
    txt = '{"__datetime__": null, "year": 1988, "month": 3, "day": 15, "hour": 8, "minute": 3, ' \
          '"second": 59, "microsecond": 7, "tzinfo": "Europe/Amsterdam", "is_dst": true}'
    obj = loads(txt)
    assert obj == pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7))


def test_tzaware_naive_date_time():
    json = dumps(DTOBJ, primitives=True)
    back = loads(json)
    for orig, bck in zip(DTOBJ, back):
        if isinstance(bck, (date, time, datetime,)):
            assert isinstance(bck, str if is_py3 else (str, unicode))
            assert bck == orig.isoformat()
        elif isinstance(bck, (timedelta,)):
            assert isinstance(bck, float)
            assert bck == orig.total_seconds()
    dt = pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7))
    assert dumps(dt, primitives=True).strip('"') == '1988-03-15T08:03:59.000007+01:00'


def test_avoiding_tz_datettime_problem():
    """
    There's a weird problem (bug? feature?) when passing timezone object to datetime constructor. This tests checks that json_tricks doesn't suffer from this problem.
    https://github.com/mverleg/pyjson_tricks/issues/41  /  https://stackoverflow.com/a/25390097/723090
    """
    tzdt = datetime(2007, 12, 5, 6, 30, 0, 1)
    tzdt = pytz.timezone('US/Pacific').localize(tzdt)
    back = loads(dumps([tzdt]))[0]
    assert pytz.utc.normalize(tzdt) == pytz.utc.normalize(back), \
        "Mismatch due to pytz localizing error {} != {}".format(
            pytz.utc.normalize(tzdt), pytz.utc.normalize(back))


def test_serialization_remains_unchanged():
    json = dumps(datetime(2023, 10, 29, 1, 30, 0, 0, pytz.UTC) \
                 .astimezone(pytz.timezone("Europe/Paris")))
    assert json == '{"__datetime__": null, "year": 2023, "month": 10, "day": 29, ' \
                   '"hour": 2, "minute": 30, "tzinfo": "Europe/Paris", "is_dst": false}'


def test_before_dst_fold():
    # issue #89
    before_dst = datetime(2023, 10, 29, 0, 30, 0, 0, pytz.UTC) \
        .astimezone(pytz.timezone("Europe/Paris"))
    back = loads(dumps(before_dst))
    assert back == before_dst
    assert back.tzinfo.zone == before_dst.tzinfo.zone
    assert back.utcoffset() == before_dst.utcoffset()


def test_after_dst_fold():
    after_dst = datetime(2023, 10, 29, 1, 30, 0, 0, pytz.UTC) \
        .astimezone(pytz.timezone("Europe/Paris"))
    back = loads(dumps(after_dst))
    assert back == after_dst
    assert back.tzinfo.zone == after_dst.tzinfo.zone
    assert back.utcoffset() == after_dst.utcoffset()
