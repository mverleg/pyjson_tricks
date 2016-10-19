
import pytz
from pytest import raises
from collections import OrderedDict
from datetime import datetime, date, time, timedelta
from .test_class import MyTestCls, CustomEncodeCls
from .nonp import strip_comments, dumps, loads, DuplicateJsonKeyException
from math import pi


nonpdata = {
	'my_array': list(range(20)),
	'my_map': {chr(k): k for k in range(97, 123)},
	'my_string': 'Hello world!',
	'my_float': 3.1415,
	'my_int': 42
}


def test_dumps_loads():
	json = dumps(nonpdata)
	data2 = loads(json)
	assert nonpdata == data2


test_json_with_comments = """{ # "comment 1
	"hello": "Wor#d", "Bye": "\\"M#rk\\"", "yes\\\\\\"": 5,# comment" 2
	"quote": "\\"th#t's\\" what she said", # comment "3"
	"list": [1, 1, "#", "\\"", "\\\\", 8], "dict": {"q": 7} #" comment 4 with quotes
}
# comment 5"""

test_json_without_comments = """{
	"hello": "Wor#d", "Bye": "\\"M#rk\\"", "yes\\\\\\"": 5,
	"quote": "\\"th#t's\\" what she said",
	"list": [1, 1, "#", "\\"", "\\\\", 8], "dict": {"q": 7}
}
"""

test_json_duplicates = """{"test": 42, "test": 37}"""


def test_strip_comments():
	valid = strip_comments(test_json_with_comments)
	assert valid == test_json_without_comments
	valid = strip_comments(test_json_with_comments.replace('#', '//'))
	assert valid == test_json_without_comments.replace('#', '//')


ordered_map = OrderedDict((
	('elephant', None),
	('chicken', None),
	('dolphin', None),
	('wild boar', None),
	('grasshopper', None),
	('tiger', None),
	('buffalo', None),
	('killer whale', None),
	('eagle', None),
	('tortoise', None),
))


def test_order():
	json = dumps(ordered_map)
	data2 = loads(json, preserve_order=True)
	assert tuple(ordered_map.keys()) == tuple(data2.keys())
	reverse = OrderedDict(reversed(tuple(ordered_map.items())))
	json = dumps(reverse)
	data3 = loads(json, preserve_order=True)
	assert tuple(reverse.keys()) == tuple(data3.keys())


cls_instance = MyTestCls(s='ub', dct={'7': 7})
cls_instance_custom = CustomEncodeCls()


def test_cls_instance_default():
	json = dumps(cls_instance)
	print(dumps(cls_instance, indent=4))
	back = loads(json)
	assert (cls_instance.s == back.s)
	assert (cls_instance.dct == dict(back.dct))


def test_cls_instance_custom():
	json = dumps(cls_instance_custom)
	back = loads(json)
	assert (cls_instance_custom.relevant == back.relevant)
	assert (cls_instance_custom.irrelevant == 37)
	assert (back.irrelevant == 12)


def test_cls_instance_local():
	json = '{"__instance_type__": [null, "CustomEncodeCls"], "attributes": {"relevant": 137}}'
	loads(json, cls_lookup_map=globals())


def test_duplicates():
	loads(test_json_duplicates, allow_duplicates=True)
	with raises(DuplicateJsonKeyException):
		loads(test_json_duplicates, allow_duplicates=False)


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


def test_complex_number():
	objs = (
		4.2 + 3.7j,
		1j,
		1 + 0j,
		-999999.9999999 - 999999.9999999j,
	)
	for obj in objs:
		json = dumps(obj)
		back = loads(json)
		assert obj == back, 'json en/decoding failed for complex number {0:}'.format(obj)
	txt = '{"__complex__": [4.2, 3.7]}'
	obj = loads(txt)
	assert obj == 4.2 + 3.7j


def test_float_precision():
	json = dumps([pi])
	back = loads(json)
	assert back[0] - pi == 0, 'Precision lost while encoding and decoding float.'


