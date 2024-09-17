#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from os.path import join
from tempfile import mkdtemp
import sys
from warnings import catch_warnings, simplefilter

from _pytest.recwarn import warns
from datetime import datetime, timezone

from numpy import arange, ones, array, array_equal, finfo, iinfo, pi
from numpy import int8, int16, int32, int64, uint8, uint16, uint32, uint64, \
	float16, float32, float64, complex64, complex128, zeros, ndindex, \
	datetime64
from numpy.core.umath import exp
from numpy.testing import assert_equal

from ro_json import numpy_encode
from ro_json.np import dump, dumps, load, loads
from ro_json.np_utils import encode_scalars_inplace
from ro_json.utils import JsonTricksDeprecation, gzip_decompress
from .test_bare import cls_instance
from .test_class import MyTestCls

DTYPES = (int8, int16, int32, int64, uint8, uint16, uint32, uint64,
	float16, float32, float64, complex64, complex128)


def get_lims(dtype):
	try:
		info = finfo(dtype)
	except ValueError:
		info = iinfo(dtype)
	return dtype(info.min), dtype(info.max)


npdata = {
	'vector': arange(15, 70, 3, dtype=uint8),
	'matrix': ones((15, 10), dtype=float64),
}


def _numpy_equality(d2):
	assert npdata.keys() == d2.keys()
	assert_equal(npdata['vector'], d2['vector'])
	assert_equal(npdata['matrix'], d2['matrix'])
	assert npdata['vector'].dtype == d2['vector'].dtype
	assert npdata['matrix'].dtype == d2['matrix'].dtype


def test_primitives():
	txt = dumps(deepcopy(npdata), primitives=True)
	data2 = loads(txt)
	assert isinstance(data2['vector'], list)
	assert isinstance(data2['matrix'], list)
	assert isinstance(data2['matrix'][0], list)
	assert data2['vector'] == npdata['vector'].tolist()
	assert (abs(array(data2['vector']) - npdata['vector'])).sum() < 1e-10
	assert data2['matrix'] == npdata['matrix'].tolist()
	assert (abs(array(data2['matrix']) - npdata['matrix'])).sum() < 1e-10


def test_dumps_loads_numpy():
	json = dumps(deepcopy(npdata))
	data2 = loads(json)
	_numpy_equality(data2)


def test_file_numpy():
	path = join(mkdtemp(), 'pytest-np.json')
	with open(path, 'wb+') as fh:
		dump(deepcopy(npdata), fh, compression=9)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	_numpy_equality(data2)


def test_compressed_to_disk():
	arr = [array([[1.0, 2.0], [3.0, 4.0]])]
	path = join(mkdtemp(), 'pytest-np.json.gz')
	with open(path, 'wb+') as fh:
		dump(arr, fh, compression=True, properties=dict(ndarray_compact=True, ndarray_store_byteorder='little'))


mixed_data = {
	'vec': array(range(10)),
	'inst': MyTestCls(
		nr=7, txt='yolo',
		li=[1, 1, 2, 3, 5, 8, 12],
		vec=array(range(7, 16, 2)),
		inst=cls_instance
	),
}


def test_mixed_cls_arr():
	json = dumps(mixed_data)
	back = dict(loads(json))
	assert mixed_data.keys() == back.keys()
	assert (mixed_data['vec'] == back['vec']).all()
	assert (mixed_data['inst'].vec == back['inst'].vec).all()
	assert (mixed_data['inst'].nr == back['inst'].nr)
	assert (mixed_data['inst'].li == back['inst'].li)
	assert (mixed_data['inst'].inst.s == back['inst'].inst.s)
	assert (mixed_data['inst'].inst.dct == dict(back['inst'].inst.dct))


def test_memory_order():
	arrC = array([[1., 2.], [3., 4.]], order='C')
	json = dumps(arrC)
	arr = loads(json)
	assert array_equal(arrC, arr)
	assert arrC.flags['C_CONTIGUOUS'] == arr.flags['C_CONTIGUOUS'] and \
		arrC.flags['F_CONTIGUOUS'] == arr.flags['F_CONTIGUOUS']
	arrF = array([[1., 2.], [3., 4.]], order='F')
	json = dumps(arrF)
	arr = loads(json)
	assert array_equal(arrF, arr)
	assert arrF.flags['C_CONTIGUOUS'] == arr.flags['C_CONTIGUOUS'] and \
		arrF.flags['F_CONTIGUOUS'] == arr.flags['F_CONTIGUOUS']


def test_array_types():
	# from: https://docs.scipy.org/doc/numpy/user/basics.types.html
	# see also `test_scalars_types`
	for dtype in DTYPES:
		vec = [array((dtype(0), dtype(exp(1))) + get_lims(dtype), dtype=dtype)]
		json = dumps(vec)
		assert dtype.__name__ in json
		rec = loads(json)
		assert rec[0].dtype == dtype
		assert array_equal(vec, rec)


def test_encode_scalar():
	encd = encode_scalars_inplace([complex128(1+2j)])
	assert isinstance(encd[0], dict)
	assert encd[0]['__ndarray__'] == 1+2j
	assert encd[0]['shape'] == ()
	assert encd[0]['dtype'] == complex128.__name__


def test_dump_np_scalars():
	data = [
		int8(-27),
		complex64(exp(1)+37j),
		(
			{
				'alpha': float64(-exp(10)),
				'str-only': complex64(-1-1j),
			},
			uint32(123456789),
			float16(exp(-1)),
			set((
				int64(37),
				uint64(-0),
			)),
		),
	]
	replaced = encode_scalars_inplace(deepcopy(data))
	json = dumps(replaced)
	rec = loads(json)
	assert data[0] == rec[0]
	assert data[1] == rec[1]
	assert data[2][0] == rec[2][0]
	assert data[2][1] == rec[2][1]
	assert data[2][2] == rec[2][2]
	assert data[2][3] == rec[2][3]
	assert data[2] == tuple(rec[2])

	json_tricks_3_17_3_encoded = '[' \
		'{"__ndarray__": -27, "dtype": "int8", "shape": []}, '\
		'{"__ndarray__": {"__complex__": [2.7182817459106445, 37.0]}, "dtype": "complex64", "shape": []}, ' \
		'[{"alpha": {"__ndarray__": -22026.465794806718, "dtype": "float64", "shape": []}, ' \
		'"str-only": {"__ndarray__": {"__complex__": [-1.0, -1.0]}, "dtype": "complex64", "shape": []}}, ' \
		'{"__ndarray__": 123456789, "dtype": "uint32", "shape": []}, ' \
		'{"__ndarray__": 0.367919921875, "dtype": "float16", "shape": []}, ' \
		'{"__set__": [{"__ndarray__": 37, "dtype": "int64", "shape": []}, ' \
		'{"__ndarray__": 0, "dtype": "uint64", "shape": []}]}]]'
	rec = loads(json_tricks_3_17_3_encoded)
	assert data[0] == rec[0]
	assert data[1] == rec[1]
	assert data[2][0] == rec[2][0]
	assert data[2][1] == rec[2][1]
	assert data[2][2] == rec[2][2]
	assert data[2][3] == rec[2][3]
	assert data[2] == tuple(rec[2])

def test_ndarray_object_nesting():
	# Based on issue 53
	# With nested ndarrays
	before = zeros((2, 2,), dtype=object)
	for i in ndindex(before.shape):
		before[i] = array([1, 2, 3])
	after = loads(dumps(before))
	assert before.shape == after.shape, \
		'shape of array changed for nested ndarrays:\n{}'.format(dumps(before, indent=2))
	assert before.dtype == before.dtype
	assert array_equal(before[0, 0], after[0, 0])
	# With nested lists
	before = zeros((2, 2,), dtype=object)
	for i in ndindex(before.shape):
		before[i] = [1, 2, 3]
	after = loads(dumps(before))
	assert before.shape == after.shape, \
		'shape of array changed for nested ndarrays:\n{}'.format(dumps(before, indent=2))
	assert before.dtype == before.dtype
	assert array_equal(before[0, 0], after[0, 0])


def test_dtype_object():
	# Based on issue 64
	arr = array(['a', 'b', 'c'], dtype=object)
	json = dumps(arr)
	back = loads(json)
	assert array_equal(back, arr)


def test_compact_mode_unspecified():
	# Other tests may have raised deprecation warning, so reset the cache here
	numpy_encode._warned_compact = False
	data = [array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]), array([pi, exp(1)])]
	with warns(JsonTricksDeprecation):
		gz_json_1 = dumps(data, compression=True)
	with catch_warnings():
		simplefilter("error")
		gz_json_2 = dumps(data, compression=True)
	assert gz_json_1 == gz_json_2
	json = gzip_decompress(gz_json_1).decode('ascii')
	assert json == '[{"__ndarray__": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]], "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": true}, ' \
		'{"__ndarray__": [3.141592653589793, 2.718281828459045], "dtype": "float64", "shape": [2], "0dim": false}]'


def test_compact():
	data = [array(list(2**(x + 0.5) for x in range(-30, +31)))]
	json = dumps(data, compression=True, properties=dict(ndarray_compact=True, ndarray_store_byteorder='little'))
	back = loads(json)
	assert_equal(data, back)


def test_encode_disable_compact():
	data = [array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]), array([pi, exp(1)])]
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=False))
	json = gzip_decompress(gz_json).decode('ascii')
	assert json == '[{"__ndarray__": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]], "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": true}, ' \
		'{"__ndarray__": [3.141592653589793, 2.718281828459045], "dtype": "float64", "shape": [2], "0dim": false}]'


def test_encode_enable_compact_little_endian():
	data = [array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]), array([pi, exp(1)])]
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=True, ndarray_store_byteorder='little'))
	json = gzip_decompress(gz_json).decode('ascii')
	assert json == '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
		 'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": ' \
		'true, "endian": "little"}, {"__ndarray__": "b64:GC1EVPshCUBpVxSLCr8FQA==", "dtype": "float64", ' \
		'"shape": [2], "0dim": false, "endian": "little"}]'


def test_encode_enable_compact_big_endian():
	data = array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=True, ndarray_store_byteorder='big'))
	json = gzip_decompress(gz_json).decode('ascii')
	assert json == '{"__ndarray__": "b64:P/AAAAAAAABAAAAAAAAAAEAIAAAAAAAAQBAAAAAAAABAFAAAAAAAAEAYAA' \
		'AAAAAAQBwAAAAAAABAIAAAAAAAAA==", "dtype": "float64", "shape": [2, 4], "0dim": false, ' \
		'"Corder": true, "endian": "big"}'


def test_encode_enable_compact_native_endian():
	data = array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=True))
	json = gzip_decompress(gz_json).decode('ascii')
	if sys.byteorder == 'little':
		assert json == '{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
 			'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": ' \
			'true, "endian": "little"}'
	elif sys.byteorder == 'big':
		assert json == '{"__ndarray__": "b64:P/AAAAAAAABAAAAAAAAAAEAIAAAAAAAAQBAAAAAAAABAFAAAAAAAAEAYAA' \
			'AAAAAAQBwAAAAAAABAIAAAAAAAAA==", "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": ' \
			'true, "endian": "big"}'
	else:
		raise Exception("unknown system endianness '{}'".format(sys.byteorder))


def test_encode_enable_compact_suppress_endianness():
	data = array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=True, ndarray_store_byteorder='suppress'))
	json = gzip_decompress(gz_json).decode('ascii')
	assert "endian" not in json


def test_encode_compact_cutoff():
	data = [array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]), array([pi, exp(1)])]
	gz_json = dumps(data, compression=True, properties=dict(ndarray_compact=5, ndarray_store_byteorder='little'))
	json = gzip_decompress(gz_json).decode('ascii')
	assert json == '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
		'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "0dim": false, "Corder": ' \
		'true, "endian": "little"}, {"__ndarray__": [3.141592653589793, 2.718281828459045], "dtype": "float64", ' \
		'"shape": [2], "0dim": false}]'


def test_encode_compact_inline_compression():
	data = [array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]])]
	json = dumps(data, compression=False, properties=dict(ndarray_compact=True, ndarray_store_byteorder='little'))
	assert 'b64.gz:' in json, 'If the overall file is not compressed and there are significant savings, then do inline gzip compression.'
	assert json == '[{"__ndarray__": "b64.gz:H4sIAAAAAAAC/2NgAIEP9gwQ4AChOKC0AJQWgdISUFoGSitAaSUorQKl1aC0BpTWgtI6UFoPShs4AABmfqWAgAAAAA==", ' \
		'"dtype": "float64", "shape": [4, 4], "0dim": false, "Corder": true, "endian": "little"}]'


def test_encode_compact_no_inline_compression():
	data = [array([[1.0, 2.0], [3.0, 4.0]])]
	json = dumps(data, compression=False, properties=dict(ndarray_compact=True, ndarray_store_byteorder='little'))
	assert 'b64.gz:' not in json, 'If the overall file is not compressed, but there are no significant savings, then do not do inline compression.'
	assert json == '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEA=", ' \
		'"dtype": "float64", "shape": [2, 2], "0dim": false, "Corder": true, "endian": "little"}]'


def test_decode_compact_mixed_compactness():
	json = '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
		'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "Corder": ' \
		'true}, {"__ndarray__": [3.141592653589793, 2.718281828459045], "dtype": "float64", "shape": [2]}]'
	data = loads(json)
	assert_equal(data[0], array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]), array([pi, exp(1)]))


def test_decode_big_endian():
	json = '{"__ndarray__": "b64:P/AAAAAAAABAAAAAAAAAAEAIAAAAAAAAQBAAAAAAAABAFAAAAAAAAEAYAA' \
		   'AAAAAAQBwAAAAAAABAIAAAAAAAAA==", "dtype": "float64", "shape": [2, 4], "Corder": ' \
		   'true, "endian": "big"}'
	data = loads(json)
	assert_equal(data, array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]))


def test_decode_little_endian():
	json = '{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
		'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "Corder": ' \
		'true, "endian": "little"}'
	data = loads(json)
	assert_equal(data, array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]))


def test_decode_without_endianness():
	json = '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEAAAAAAAAA' \
		'UQAAAAAAAABhAAAAAAAAAHEAAAAAAAAAgQA==", "dtype": "float64", "shape": [2, 4], "Corder": true}]'
	data = loads(json)
	if sys.byteorder == 'big':
		import pytest
		pytest.skip('skip for big endian systems')
	assert_equal(data[0], array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]))


def test_decode_compact_inline_compression():
	json = '[{"__ndarray__": "b64.gz:H4sIAAAAAAAC/2NgAIEP9gwQ4AChOKC0AJQWgdISUFoGSitAaSUorQKl1aC0BpTWgtI6UFoPShs4AABmfqWAgAAAAA==", "dtype": "float64", "shape": [4, 4], "Corder": true}]'
	data = loads(json)
	assert_equal(data[0], array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]]))


def test_decode_compact_no_inline_compression():
	json = '[{"__ndarray__": "b64:AAAAAAAA8D8AAAAAAAAAQAAAAAAAAAhAAAAAAAAAEEA=", ' \
		'"dtype": "float64", "shape": [2, 2], "Corder": true}]'
	data = loads(json)
	assert_equal(data[0], array([[1.0, 2.0], [3.0, 4.0]]))


def test_empty():
	# issue https://github.com/mverleg/pyjson_tricks/issues/76
	datas = [
		zeros(shape=(1, 0)),
		zeros(shape=(0, 1)),
		zeros(shape=(0, 0)),
	]
	for data in datas:
		json = dumps(data)
		assert_equal(loads(json), data, 'shape = {} ; json = {}'.format(data.shape, json))

def test_decode_writeable():
	# issue https://github.com/mverleg/pyjson_tricks/issues/90
	data = zeros((2, 2))

	data_uncompressed = dumps(data)
	data_compressed = dumps(data, properties={'ndarray_compact': True})

	reloaded_uncompressed = loads(data_uncompressed)
	reloaded_compressed = loads(data_compressed)

	assert array_equal(data, reloaded_uncompressed)
	assert array_equal(data, reloaded_compressed)

	assert reloaded_uncompressed.flags.writeable
	assert reloaded_compressed.flags.writeable


def test_0_dimensional_array_roundtrip():
	to_dump = zeros((), dtype='uint32')
	to_dump[...] = 123

	the_dumps = dumps(to_dump)
	loaded = loads(the_dumps)
	assert loaded == to_dump

	the_double_dumps = dumps(loaded)
	assert the_dumps == the_double_dumps


def test_0_dimensional_array_roundtrip_object():
	the_set = set([1, 2, 3])

	# We are putting it an object in a numpy array. this should serialize correctly
	to_dump = zeros((), dtype=object)
	to_dump[...] = the_set

	the_dumps = dumps(to_dump)
	the_load = loads(the_dumps)
	the_double_dumps = dumps(the_load)

	assert the_dumps == the_double_dumps

	assert isinstance(the_load[()], set)
	assert the_set == the_load[()]


def test_scalar_roundtrip():
	to_dump = [
		uint8(1),
		uint16(2),
		uint32(3),
		uint64(4),
		int8(1),
		int16(2),
		int32(3),
		int64(4),
		float32(1),
		float64(2),
	]

	the_dumps = dumps(to_dump)
	the_load = loads(the_dumps)

	for original, read in zip(to_dump, the_load):
		assert original == read
		assert original.__class__ == read.__class__

	the_double_dumps = dumps(loads(dumps(to_dump)))

	assert the_dumps == the_double_dumps


def test_round_trip_datetime64_scalars():
	now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
	now_M = datetime64(now_utc, 'M')
	now_D = datetime64(now_utc, 'D')
	now_h = datetime64(now_utc, 'h')
	now_m = datetime64(now_utc, 'm')
	now_s = datetime64(now_utc, 's')
	now_ms = datetime64(now_utc, 'ms')
	now_us = datetime64(now_utc, 'us')
	now_ns = datetime64(now_utc, 'ns')

	to_dump = [
		now_M,
		now_D,
		now_h,
		now_m,
		now_s,
		now_ms,
		now_us,
		now_ns,
		now_us,
		now_ns,
	]

	the_dumps = dumps(to_dump)
	the_load = loads(the_dumps)

	for original, read in zip(to_dump, the_load):
		assert original == read
		assert original.__class__ == read.__class__
		assert original.dtype == read.dtype

	the_double_dumps = dumps(loads(dumps(to_dump)))

	assert the_dumps == the_double_dumps
