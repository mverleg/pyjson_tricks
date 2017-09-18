#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests timezone-aware date/time objects, which need pytz. Naive date/times should
work with just Python code functionality, and are tested in `nonp`.
"""

from datetime import datetime, date, time, timedelta
from time import struct_time, localtime
from json_tricks import dumps, loads
from json_tricks.nonp import is_py3
import pytz


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


def test_struct_time():
	datemin, datemax = date(year=1, month=1, day=1).timetuple(), date(year=+5000, month=12, day=31).timetuple()
	for tmstrct in [localtime(),
			struct_time((1, 1, 1, 0, 0, 0, datemin.tm_wday, datemin.tm_yday, 0)),
			struct_time((+5000, 12, 31, 23, 59, 59, datemin.tm_yday, datemin.tm_yday, 1))]:
		json = dumps(tmstrct)
		back = loads(json)
		print("JSON: " + json)   # todo
		assert tmstrct == back


