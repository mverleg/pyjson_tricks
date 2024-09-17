#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ro_json.utils import hashodict, get_arg_names, nested_index


def test_hashodict():
	data = hashodict((('alpha', 37), ('beta', 42), ('gamma', -99)))
	assert tuple(data.keys()) == ('alpha', 'beta', 'gamma',)
	assert isinstance(hash(data), int)


def test_get_args():
	def get_my_args(hello, world=7):
		pass
	argnames = get_arg_names(get_my_args)
	assert argnames == set(('hello', 'world'))


def test_nested_index():
	arr = [[[1, 2], [1, 2]], [[1, 2], [3, 3]]]
	assert 1 == nested_index(arr, (0, 0, 0,))
	assert 2 == nested_index(arr, (1, 0, 1,))
	assert [1, 2] == nested_index(arr, (1, 0,))
	assert [3, 3] == nested_index(arr, (1, 1,))
	assert [[1, 2], [1, 2]] == nested_index(arr, (0,))
	assert [[[1, 2], [1, 2]], [[1, 2], [3, 3]]] == nested_index(arr, ())
	try:
		nested_index(arr, (0, 0, 0, 0,))
	except TypeError:
		pass
	else:
		raise AssertionError('indexing more than nesting level should yield IndexError')


def base85_vsbase64_performance():
	from base64 import b85encode, standard_b64encode, urlsafe_b64encode
	from random import getrandbits
	test_data = bytearray(getrandbits(8) for _ in range(10000000))
	from timeit import default_timer
	print('')

	start = default_timer()
	for _ in range(20):
		standard_b64encode(test_data)
	end = default_timer()
	print('standard_b64encode took {} s'.format(end - start))

	start = default_timer()
	for _ in range(20):
		urlsafe_b64encode(test_data)
	end = default_timer()
	print('urlsafe_b64encode took {} s'.format(end - start))

	start = default_timer()
	for _ in range(20):
		b85encode(test_data)
	end = default_timer()
	print('b85encode took {} s'.format(end - start))

	# Result on local PC in 2020: base84 is 53x slower to encode
	# (urlsafe also costs a bit of performance, about 2x)
