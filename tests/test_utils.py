#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json_tricks.utils import hashodict, get_arg_names, nested_index


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
