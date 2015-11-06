
from collections import OrderedDict
from tempfile import mkdtemp
from numpy import arange, ones, uint8, float64
from os.path import join
from json_tricks import strip_hash_comments, dumps, loads, dump, load


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
	valid = strip_hash_comments(test_json_with_comments)
	assert valid == test_json_without_comments


npdata = {
	'vector': arange(15, 70, 3, dtype=uint8),
	'matrix': ones((15, 10), dtype=float64),
}


def test_dumps_loads_numpy():
	json = dumps(npdata)
	data2 = loads(json)
	assert npdata.keys() == data2.keys()
	assert (npdata['vector'] == data2['vector']).all()
	assert (npdata['matrix'] == data2['matrix']).all()
	assert npdata['vector'].dtype == data2['vector'].dtype
	assert npdata['matrix'].dtype == data2['matrix'].dtype


def test_dump_load_numpy():
	path = join(mkdtemp(), 'pytest.json')
	with open(path, 'wb+') as fh:
		dump(npdata, fh, compression=9)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	assert npdata.keys() == data2.keys()
	assert (npdata['vector'] == data2['vector']).all()
	assert (npdata['matrix'] == data2['matrix']).all()
	assert npdata['vector'].dtype == data2['vector'].dtype
	assert npdata['matrix'].dtype == data2['matrix'].dtype


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


