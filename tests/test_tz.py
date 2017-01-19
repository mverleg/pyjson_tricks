
from datetime import datetime, date, time, timedelta
from json_tricks import dumps, loads
import pytz
from json_tricks.nonp import is_py3


DTOBJS = (
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


def test_date_time():
	for obj in DTOBJS:
		json = dumps(obj)
		back = loads(json)
		assert obj == back, 'json en/decoding failed for date/time object {0:}'.format(obj)
	txt = '{"__datetime__": null, "year": 1988, "month": 3, "day": 15, "hour": 8, "minute": 3, ' \
		'"second": 59, "microsecond": 7, "tzinfo": "Europe/Amsterdam"}'
	obj = loads(txt)
	assert obj == datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))


def test_approximate_type_date_time():
	for obj in DTOBJS:
		json = dumps(obj, primitives=True)
		back = loads(json)
		if isinstance(obj, (date, time, datetime,)):
			assert isinstance(back, str if is_py3 else (str, unicode))
			assert back == obj.isoformat()
		elif isinstance(obj, (timedelta,)):
			assert isinstance(back, float)
			assert back == obj.total_seconds()
	dt = datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7, tzinfo=pytz.timezone('Europe/Amsterdam'))
	assert dumps(dt, primitives=True).strip('"') == '1988-03-15T08:03:59.000007+00:20'


