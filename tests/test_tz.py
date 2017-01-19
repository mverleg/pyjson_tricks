
from datetime import datetime, date, time, timedelta
from json_tricks import dumps, loads
import pytz


def test_date_time():
	objs = (
		datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7),
		datetime(year=1988, month=3, day=15, minute=3, second=59, microsecond=7, tzinfo=pytz.UTC),
		datetime(year=1988, month=3, day=15, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam')),
		date(year=1988, month=3, day=15),
		time(hour=8, minute=3, second=59, microsecond=123),
		time(hour=8, second=59, microsecond=123, tzinfo=pytz.timezone('Europe/Amsterdam')),
		timedelta(days=2, seconds=3599),
		timedelta(days=0, seconds=-42, microseconds=123),
		[{'obj': [datetime(year=1988, month=3, day=15, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))]}],
	)
	for obj in objs:
		json = dumps(obj)
		back = loads(json)
		assert obj == back, 'json en/decoding failed for date/time object {0:}'.format(obj)
	txt = '{"__datetime__": null, "year": 1988, "month": 3, "day": 15, "hour": 8, "minute": 3, ' \
		'"second": 59, "microsecond": 7, "tzinfo": "Europe/Amsterdam"}'
	obj = loads(txt)
	assert obj == datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))


