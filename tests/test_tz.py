#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests timezone-aware date/time objects, which need pytz. Naive date/times should
work with just Python code functionality, and are tested in `nonp`.
"""

from datetime import datetime, date, time, timedelta
from json_tricks import dumps, loads
import pytz
from json_tricks.nonp import is_py3


DTOBJ = [
	datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7),
	datetime(year=1988, month=3, day=15, minute=3, second=59, microsecond=7, tzinfo=pytz.UTC),
	datetime(year=1988, month=3, day=15, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam')),
	date(year=1988, month=3, day=15),
	time(hour=8, minute=3, second=59, microsecond=123),
	time(hour=8, second=59, microsecond=123, tzinfo=pytz.timezone('Europe/Amsterdam')),
	timedelta(days=2, seconds=3599),
	timedelta(days=0, seconds=-42, microseconds=123),
	[{'obj': [datetime(year=1988, month=3, day=15, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))]}],
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
	assert obj == datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))


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
	dt = datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))
	assert dumps(dt, primitives=True).strip('"') == '1988-03-15T08:03:59.000007+00:20'


