
from collections import OrderedDict
from .nonp import strip_comments, dumps, loads


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
	json = dumps(ordered_map, preserve_order=True)
	data2 = loads(json, preserve_order=True)
	assert tuple(ordered_map.keys()) == tuple(data2.keys())
	reverse = OrderedDict(reversed(tuple(ordered_map.items())))
	json = dumps(reverse, preserve_order=True)
	data3 = loads(json, preserve_order=True)
	assert tuple(reverse.keys()) == tuple(data3.keys())


