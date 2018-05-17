#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests timezone-aware date/time objects, which need pytz. Naive date/times should
work with just Python code functionality, and are tested in `nonp`.
"""

from datetime import datetime, date, time, timedelta
from json_tricks import dumps, loads
from json_tricks.utils import is_py3
import pytz


DTOBJ = [
	datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7),
	pytz.UTC.localize(datetime(year=1988, month=3, day=15, minute=3, second=59, microsecond=7)),
	pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, microsecond=7)),
	date(year=1988, month=3, day=15),
	time(hour=8, minute=3, second=59, microsecond=123),
	time(hour=8, second=59, microsecond=123, tzinfo=pytz.timezone('Europe/Amsterdam')),
	timedelta(days=2, seconds=3599),
	timedelta(days=0, seconds=-42, microseconds=123),
	[{'obj': [pytz.timezone('Europe/Amsterdam').localize(datetime(year=1988, month=3, day=15, microsecond=7))]}],
]


def test_tzaware_date_time():
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


