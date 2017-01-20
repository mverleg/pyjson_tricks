#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json_tricks.utils import hashodict, get_arg_names


def test_hashodict():
	data = hashodict((('alpha', 37), ('beta', 42), ('gamma', -99)))
	assert tuple(data.keys()) == ('alpha', 'beta', 'gamma',)
	assert isinstance(hash(data), int)


def test_get_args():
	def get_my_args(hello, world=7):
		pass
	argnames = get_arg_names(get_my_args)
	assert argnames == set(('hello', 'world'))


