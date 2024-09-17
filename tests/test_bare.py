#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, time, date, timedelta
from decimal import Decimal
from fractions import Fraction
from functools import partial
from io import BytesIO, StringIO
from math import pi, exp
from os.path import join
from tempfile import mkdtemp
from warnings import catch_warnings, simplefilter

import pytest
from pytest import raises, fail, warns

from ro_json import fallback_ignore_unknown, DuplicateJsonKeyException
from ro_json.nonp import strip_comments, dump, dumps, load, loads, \
	ENCODING
from ro_json.utils import is_py3, gzip_compress, JsonTricksDeprecation, str_type
from .test_class import MyTestCls, CustomEncodeCls, SubClass, SuperClass, SlotsBase, SlotsDictABC, SlotsStr, \
	SlotsABCDict, SlotsABC

nonpdata = {
	'my_array': list(range(20)),
	'my_map': dict((chr(k), k) for k in range(97, 123)),
	'my_string': 'Hello world!',
	'my_float': 3.1415,
	'my_int': 42
}


def test_dumps_loads():
	json = dumps(nonpdata)
	data2 = loads(json)
	assert nonpdata == data2


def test_file_handle():
	path = join(mkdtemp(), 'pytest-nonp.json')
	with open(path, 'wb+') as fh:
		dump(nonpdata, fh, compression=6)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	assert data2 == nonpdata
	with open(path, 'rb') as fh:
		data3 = load(fh, decompression=None)  # test autodetect gzip
	assert data3 == nonpdata


def test_mix_handle_str_path():
	# Based on issue 68
	data = {"fun": 1.1234567891234567e-13}
	path = join(mkdtemp(), 'test_mix_handle_str_path.json')
	dump(data, open(path, "w"))
	back = load(path)
	assert data == back


def test_wrong_arg_order():
	# Based on a problem from https://github.com/mverleg/array_storage_benchmark
	li = [[1.0, 2.0], [3.0, 4.0]]
	map = {"a": 1}
	path = join(mkdtemp(), 'pytest-np.json.gz')
	msg = 'json-tricks dump arguments are in the wrong order: provide the data to be serialized before file handle'
	with raises(ValueError) as ex:
		with open(path, 'wb+') as fh:
			dump(fh, li)
	assert msg in ex.value.args[0]
	with raises(ValueError) as ex:
		dump(path, li)
	assert msg in ex.value.args[0]
	with raises(ValueError) as ex:
		with open(path, 'wb+') as fh:
			dump(fh, map)
	assert msg in ex.value.args[0]
	with raises(ValueError) as ex:
		dump(path, map)
	assert msg in ex.value.args[0]


def test_mix_handle_bin_path():
	# Based on issue 68
	data = {"fun": 1.1234567891234567e-13}
	path = join(mkdtemp(), 'test_mix_handle_bin_path.json')
	if is_py3:
		with raises(TypeError):
			dump(data, open(path, "wb"))


def test_mix_path_handle():
	# Based on issue 68
	data = {"fun": 1.1234567891234567e-13}
	path = join(mkdtemp(), 'test_mix_path_handle.json')
	dump(data, path)


def test_file_handle_types():
	path = join(mkdtemp(), 'pytest-text.json')
	for conv_str_byte in [True, False]:
		with open(path, 'w+') as fh:
			dump(nonpdata, fh, compression=False, conv_str_byte=conv_str_byte)
		with open(path, 'r') as fh:
			assert load(fh, conv_str_byte=conv_str_byte) == nonpdata
		with StringIO() as fh:
			dump(nonpdata, fh, conv_str_byte=conv_str_byte)
			fh.seek(0)
			assert load(fh, conv_str_byte=conv_str_byte) == nonpdata
	with BytesIO() as fh:
		with raises(TypeError):
			dump(nonpdata, fh)
	with BytesIO() as fh:
		dump(nonpdata, fh, conv_str_byte=True)
		fh.seek(0)
		assert load(fh, conv_str_byte=True) == nonpdata
	if is_py3:
		with open(path, 'w+') as fh:
			with raises(IOError):
				dump(nonpdata, fh, compression=6)


def test_file_path():
	path = join(mkdtemp(), 'pytest-nonp.json')
	dump(nonpdata, path, compression=6)
	data2 = load(path, decompression=True)
	assert data2 == nonpdata
	data3 = load(path, decompression=None)  # autodetect gzip
	assert data3 == nonpdata


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

test_object_for_comment_strings = {
	"hello": "Wor#d", "Bye": "\"M#rk\"", "yes\\\"": 5,
	"quote": "\"th#t's\" what she said",
	"list": [1, 1, "#", "\"", "\\", 8], "dict": {"q": 7}
}

test_json_duplicates = """{"test": 42, "test": 37}"""


def test_strip_comments():
	valid = strip_comments(test_json_with_comments)
	assert valid == test_json_without_comments
	valid = strip_comments(test_json_with_comments.replace('#', '//'))
	assert valid == test_json_without_comments.replace('#', '//')


def test_ignore_comments_deprecation():
	# https://github.com/mverleg/pyjson_tricks/issues/74

	# First time should have deprecation warning
	loads._ignore_comments_warned_ = False
	with warns(JsonTricksDeprecation):
		loads(test_json_with_comments)

	# Second time there should be no warning
	with catch_warnings():
		simplefilter("error")
		loaded = loads(test_json_with_comments)
	assert loaded == test_object_for_comment_strings

	# Passing a string without comments should not have a warning
	loads._ignore_comments_warned_ = False
	with catch_warnings():
		simplefilter("error")
		loaded = loads(test_json_without_comments)

	# Passing True for argument explicitly should not have a warning
	loads._ignore_comments_warned_ = False
	with catch_warnings():
		simplefilter("error")
		loaded = loads(test_json_with_comments, ignore_comments=True)
	assert loaded == test_object_for_comment_strings

	# Passing False for argument explicitly should not have a warning
	loads._ignore_comments_warned_ = False
	with catch_warnings():
		simplefilter("error")
		loaded = loads(test_json_without_comments, ignore_comments=False)
	assert loaded == test_object_for_comment_strings


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


def test_string_compression():
	json = dumps(ordered_map, compression=3)
	assert json[:2] == b'\x1f\x8b'
	data2 = loads(json, decompression=True)
	assert ordered_map == data2
	data3 = loads(json, decompression=None)
	assert ordered_map == data3


def test_flush_no_errors():
	# just tests that flush doesn't cause problems; checking actual flushing is too messy.
	path = join(mkdtemp(), 'pytest-nonp.json')
	with open(path, 'wb+') as fh:
		dump(nonpdata, fh, compression=True, force_flush=True)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	assert data2 == nonpdata
	# flush non-file IO
	sh = BytesIO()
	try:
		dump(ordered_map, fp=sh, compression=True, force_flush=True)
	finally:
		sh.close()


def test_compression_with_comments():
	if is_py3:
		test_json = bytes(test_json_with_comments, encoding=ENCODING)
	else:
		test_json = test_json_with_comments
	json = gzip_compress(test_json, compresslevel=9)
	ref = loads(test_json_without_comments)
	data2 = loads(json, decompression=True)
	assert ref == data2
	data3 = loads(json, decompression=None)
	assert ref == data3


def test_hooks_called_once_if_no_comments():
	call_count = [0]
	def counting_hook(obj, *args):
		call_count[0] += 1
		return obj
	result = loads('{"abc": 123}', ignore_comments=None, extra_obj_pairs_hooks=(counting_hook,))
	assert result == {"abc": 123}
	assert call_count[0] == 1


def test_hooks_called_once_if_comment_before():
	call_count = [0]
	def counting_hook(obj, *args):
		call_count[0] += 1
		return obj
	result = loads('// comment\n{"abc": 123}', ignore_comments=None, extra_obj_pairs_hooks=(counting_hook,))
	assert result == {"abc": 123}
	assert call_count[0] == 1


def test_hooks_called_twice_if_comment_after():
	call_count = [0]
	def counting_hook(obj, *args):
		call_count[0] += 1
		return obj
	result = loads('{"abc": 123} // comment', ignore_comments=None, extra_obj_pairs_hooks=(counting_hook,))
	assert result == {"abc": 123}
	assert call_count[0] == 2


def test_order():
	json = dumps(ordered_map)
	data2 = loads(json, preserve_order=True)
	assert tuple(ordered_map.keys()) == tuple(data2.keys())
	reverse = OrderedDict(reversed(tuple(ordered_map.items())))
	json = dumps(reverse)
	data3 = loads(json, preserve_order=True)
	assert tuple(reverse.keys()) == tuple(data3.keys())
	json = dumps(ordered_map)
	data4 = loads(json, preserve_order=False)
	assert not isinstance(data4, OrderedDict)


cls_instance = MyTestCls(s='ub', dct={'7': 7})
cls_instance_custom = CustomEncodeCls()


def test_cls_instance_default():
	json = dumps(cls_instance)
	back = loads(json)
	assert (cls_instance.s == back.s)
	assert (cls_instance.dct == dict(back.dct))
	json = dumps(cls_instance, primitives=True)
	back = loads(json)
	assert tuple(sorted(back.keys())) == ('dct', 's',)
	assert '7' in back['dct']


def test_cls_instance_custom():
	json = dumps(cls_instance_custom)
	back = loads(json)
	assert (cls_instance_custom.relevant == back.relevant)
	assert (cls_instance_custom.irrelevant == 37)
	assert (back.irrelevant == 12)
	json = dumps(cls_instance_custom, primitives=True)
	back = loads(json)
	assert (cls_instance_custom.relevant == back['relevant'])
	assert (cls_instance_custom.irrelevant == 37)
	assert 'irrelevant' not in back


def test_cls_instance_local():
	json = '{"__instance_type__": [null, "CustomEncodeCls"], "attributes": {"relevant": 137}}'
	loads(json, cls_lookup_map=globals())


def test_cls_instance_inheritance():
	inst = SubClass()
	json = dumps(inst)
	assert '42' not in json
	back = loads(json)
	assert inst == back
	inst.set_attr()
	json = dumps(inst)
	assert '42' in json
	back = loads(json)
	assert inst == back


def test_cls_attributes_unchanged():
	"""
	Test that class attributes are not restored. This would be undesirable,
	because deserializing one instance could impact all other existing ones.
	"""
	SuperClass.cls_attr = 37
	inst = SuperClass()
	json = dumps(inst)
	assert '37' not in json
	SuperClass.cls_attr = 42
	back = loads(json)
	assert inst == back
	assert inst.cls_attr == back.cls_attr == 42
	SuperClass.cls_attr = 37


def test_cls_lookup_map_fail():
	class LocalCls(object):
		def __init__(self, val):
			self.value = val
	original = [LocalCls(37), LocalCls(42)]
	txt = dumps(original)
	with raises(ImportError) as err:
		loads(txt)
	assert 'LocalCls' in str(err.value)
	assert 'cls_lookup_map' in str(err.value)
	with raises(ImportError) as err:
		loads(txt, cls_lookup_map=globals())
	assert 'LocalCls' in str(err.value)
	assert 'cls_lookup_map' in str(err.value)


def test_cls_lookup_map_success():
	class LocalCls(object):
		def __init__(self, val):
			self.value = val
	original = [LocalCls(37), LocalCls(42)]
	txt = dumps(original)
	back = loads(txt, cls_lookup_map=dict(LocalCls=LocalCls))
	assert len(original) == len(back) == 2
	assert original[0].value == back[0].value
	assert original[1].value == back[1].value
	back = loads(txt, properties=dict(cls_lookup_map=dict(LocalCls=LocalCls)))
	assert len(original) == len(back) == 2
	assert original[0].value == back[0].value
	assert original[1].value == back[1].value


def test_cls_slots():
	slots = [SlotsBase(), SlotsDictABC(), SlotsStr(), SlotsABCDict(), SlotsABC()]
	txt = dumps(slots)
	res = loads(txt)
	for inputobj, outputobj in zip(slots, res):
		assert isinstance(outputobj, SlotsBase)
		assert inputobj == outputobj
	referenceobj = SlotsBase()
	for outputobj in res[1:]:
		assert outputobj != referenceobj


def test_duplicates():
	loads(test_json_duplicates, allow_duplicates=True)
	with raises(DuplicateJsonKeyException):
		loads(test_json_duplicates, allow_duplicates=False)


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
		assert back == obj, 'json en/decoding failed for complex number {0:}'.format(obj)
		json = dumps(obj, primitives=True)
		back = loads(json)
		assert back == [obj.real, obj.imag]
		assert complex(*back) == obj
	txt = '{"__complex__": [4.2, 3.7]}'
	obj = loads(txt)
	assert obj == 4.2 + 3.7j


def test_float_precision():
	json = dumps([pi])
	back = loads(json)
	assert back[0] - pi == 0, 'Precision lost while encoding and decoding float.'


def test_set():
	setdata = [{'set': set((3, exp(1), (-5, +7), False))}]
	json = dumps(setdata)
	back = loads(json)
	assert isinstance(back[0]['set'], set)
	assert setdata == back
	json = dumps(setdata, primitives=True)
	back = loads(json)
	assert isinstance(back[0]['set'], list)
	assert setdata[0]['set'] == set(tuple(q) if isinstance(q, list) else q for q in back[0]['set'])


def test_special_nr_parsing():
	nr_li_json = '[1, 3.14]'
	res = loads(nr_li_json,
		parse_int=lambda s: int('7' + s),
		parse_float=lambda s: float('5' + s)
	)
	assert res == [71, 53.14], 'Special integer and/or float parsing not working'
	nr_li_json = '[1, 3.14]'
	res = loads(nr_li_json,
		parse_int=Decimal,
		parse_float=Decimal
	)
	assert isinstance(res[0], Decimal)
	assert isinstance(res[1], Decimal)


def test_special_floats():
	"""
	The official json standard doesn't support infinity or NaN, but the Python implementation does.
	"""
	special_floats = [float('NaN'), float('Infinity'), -float('Infinity'), float('+0'), float('-0')]
	txt = dumps(special_floats, allow_nan=True)
	assert txt == "[NaN, Infinity, -Infinity, 0.0, -0.0]"
	res = loads(txt)
	for x, y in zip(special_floats, res):
		""" Use strings since `+0 == -1` and `NaN != NaN` """
		assert str(x) == str(y)
	with raises(ValueError):
		dumps(special_floats, allow_nan=False)
	with raises(ValueError):
		dumps(special_floats)


def test_decimal():
	decimals = [Decimal(0), Decimal(-pi), Decimal('9999999999999999999999999999999999999999999999999999'),
		Decimal('NaN'), Decimal('Infinity'), -Decimal('Infinity'), Decimal('+0'), Decimal('-0')]
	txt = dumps(decimals)
	res = loads(txt)
	for x, y in zip(decimals, res):
		assert isinstance(y, Decimal)
		assert x == y or x.is_nan()
		assert str(x) == str(y)


def test_decimal_primitives():
	decimals = [Decimal(0), Decimal(-pi), Decimal('9999999999999')]
	txt = dumps(decimals, primitives=True)
	res = loads(txt)
	for x, y in zip(decimals, res):
		assert isinstance(y, float)
		assert x == y or x.is_nan()


def test_fraction():
	fractions = [Fraction(0), Fraction(1, 3), Fraction(-pi), Fraction('1/3'), Fraction('1/3') / Fraction('1/6'),
		Fraction('9999999999999999999999999999999999999999999999999999'), Fraction('1/12345678901234567890123456789'),]
	txt = dumps(fractions)
	res = loads(txt)
	for x, y in zip(fractions, res):
		assert isinstance(y, Fraction)
		assert x == y
		assert str(x) == str(y)
	txt = dumps(fractions, primitives=True)
	res = loads(txt)
	for x, y in zip(fractions, res):
		assert isinstance(y, float)
		assert abs(x - y) < 1e-10


DTOBJ = [
	datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7),
	date(year=1988, month=3, day=15),
	time(hour=8, minute=3, second=59, microsecond=123),
	timedelta(days=2, seconds=3599),
]


def test_naive_date_time():
	json = dumps(DTOBJ)
	back = loads(json)
	assert DTOBJ == back
	for orig, bck in zip(DTOBJ, back):
		assert orig == bck
		assert type(orig) == type(bck)
	txt = '{"__datetime__": null, "year": 1988, "month": 3, "day": 15, "hour": 8, "minute": 3, ' \
			'"second": 59, "microsecond": 7}'
	obj = loads(txt)
	assert obj == datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7)


def test_primitive_naive_date_time():
	json = dumps(DTOBJ, primitives=True)
	back = loads(json)
	for orig, bck in zip(DTOBJ, back):
		if isinstance(bck, (date, time, datetime,)):
			assert isinstance(bck, str_type)
			assert bck == orig.isoformat()
		elif isinstance(bck, (timedelta,)):
			assert isinstance(bck, float)
			assert bck == orig.total_seconds()
	dt = datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7)
	assert dumps(dt, primitives=True).strip('"') == '1988-03-15T08:03:59.000007'


def test_str_unicode_bytes():
	text, obj = u'{"mykey": "你好"}', {"mykey": u"你好"}
	assert loads(text) == obj
	if is_py3:
		with raises(TypeError) as err:
			loads(text.encode('utf-8'))
		if 'ExceptionInfo' in str(type(err)):
			# This check is needed because the type of err varies between versions
			# For some reason, isinstance(..., py.code.ExceptionInfo) does not work
			err = err.value
		assert 'The input was of non-string type' in str(err)
		assert loads(text.encode('utf-8'), conv_str_byte=True) == obj
	else:
		assert loads('{"mykey": "nihao"}') == {'mykey': 'nihao'}


def with_nondict_hook():
	""" Add a custom hook, to test that all future hooks handle non-dicts. """
	# Prevent issue 26 from coming back.
	def test_hook(dct):
		if not isinstance(dct, dict):
			return
		return ValueError()
	loads('{"key": 42}', extra_obj_pairs_hooks=(test_hook,))


def test_custom_enc_dec():
	""" Test using a custom encoder/decoder. """
	def silly_enc(obj):
		return {"val": 42}
	def silly_dec(dct):
		if not isinstance(dct, dict):
			return dct
		return [37]
	txt = dumps(lambda x: x * 2, extra_obj_encoders=(silly_enc,))
	assert txt == '{"val": 42}'
	back = loads(txt, extra_obj_pairs_hooks=(silly_dec,))
	assert back == [37]


def test_lambda_partial():
	""" Test that a custom encoder/decoder works when wrapped in functools.partial,
		which caused problems before because inspect.getargspec does not support it. """
	obj = dict(alpha=37.42, beta=[1, 2, 4, 8, 16, 32])
	enc_dec_lambda = partial(lambda x, y: x, y=0)
	txt = dumps(obj, extra_obj_encoders=(enc_dec_lambda,))
	back = loads(txt, extra_obj_pairs_hooks=(enc_dec_lambda,))
	assert obj == back
	def enc_dec_fun(obj, primitives=False, another=True):
		return obj
	txt = dumps(obj, extra_obj_encoders=(partial(enc_dec_fun, another=True),))
	back = loads(txt, extra_obj_pairs_hooks=(partial(enc_dec_fun, another=True),))
	assert obj == back


def test_hooks_not_too_eager():
	from threading import RLock
	with raises(TypeError):
		dumps([RLock()])
		# TypeError did not get raised, so show a message
		# (https://github.com/pytest-dev/pytest/issues/3974)
		fail('There is no hook to serialize RLock, so this should fail, '
			'otherwise some hook is too eager.')


def test_fallback_hooks():
	from threading import RLock

	json = dumps(OrderedDict((
		('li', [1, 2, 3]),
		('lock', RLock()),
	)), fallback_encoders=[fallback_ignore_unknown])
	bck = loads(json)
	assert bck == OrderedDict((
		('li', [1, 2, 3]),
		('lock', None),
	))


def test_empty_string_with_url():
	""" Originally for https://github.com/mverleg/pyjson_tricks/issues/51 """
	txt = '{"foo": "", "bar": "http://google.com"}'
	assert txt == strip_comments(txt), strip_comments(txt)
	txt = '{"foo": "", "bar": "http://google.com"}'
	assert txt == dumps(loads(txt, ignore_comments=False))
	assert txt == dumps(loads(txt, ignore_comments=True))
	txt = '{"a": "", "b": "//", "c": ""}'
	assert txt == dumps(loads(txt))
	txt = '{"a": "", "b": "/*", "c": ""}'
	assert txt == dumps(loads(txt))
	txt = '{"//": "//"}'
	assert txt == dumps(loads(txt))
	txt = '{"///": "////*/*"}'
	assert txt == dumps(loads(txt))


def test_no_cls():
	""" Originally for https://github.com/mverleg/pyjson_tricks/issues/79 """
	data = dict(name='Leonardo da Vinci', year=1452)
	path = join(mkdtemp(), 'pytest-no-cls.json')
	with open(path, 'wb+') as fh:
		dump(data, fh, cls=None, compression=1)
	with open(path, 'rb') as fh:
		bck = load(fh)
	assert data == bck
	txt = dumps(data, cls=None, compression=2)
	bck = loads(txt)
	assert data == bck


@pytest.mark.skipif(condition=not is_py3, reason='encoding bytes not supported on python 2')
def test_utf8_bytes():
	inputs = [
		b'hello world',
		b'',
		b'\n',
		u'你好'.encode('utf-8', 'ignore'),
		b'"',
		b"''",
	]
	json = dumps(inputs)
	assert '__bytes_utf8__' in json
	assert '__bytes_b64__' not in json
	json_bytes = json.encode('utf-8', 'ignore')
	assert inputs[0] in json_bytes
	bck = loads(json)
	assert inputs == bck


@pytest.mark.skipif(condition=not is_py3, reason='encoding bytes not supported on python 2')
def test_nonutf8_bytes():
	inputs = [
		b'\xc3\x28',
		b'\xa0\xa1',
		b'\xe2\x28\xa1',
		b'\xe2\x82\x28',
		b'\xf0\x28\x8c\xbc',
		b'\xf0\x90\x28\xbc',
		b'\xf0\x28\x8c\x28',
	]
	json = dumps(inputs)
	assert '__bytes_utf8__' not in json
	assert '__bytes_b64__' in json
	json_bytes = json.encode('utf-8', 'ignore')
	for input in inputs:
		assert input not in json_bytes
	bck = loads(json)
	assert inputs == bck


@pytest.mark.skipif(condition=not is_py3, reason='encoding bytes not supported on python 2')
def test_bytes_primitive_repr():
	inp = [u'hello = 你好'.encode('utf-8', 'ignore')]
	assert inp[0] == b'hello = \xe4\xbd\xa0\xe5\xa5\xbd'
	json = dumps(inp, primitives=True)
	assert json == '[{"__bytes_b64__": "aGVsbG8gPSDkvaDlpb0="}]'
	bck = loads(json)
	assert inp == bck

