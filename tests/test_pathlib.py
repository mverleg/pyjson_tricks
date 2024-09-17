#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests Paths, which need pathlib.
"""

from pathlib import Path

from ro_json import dumps, loads


# These paths are not necessarily actual paths that exist, but are sufficient
# for testing to ensure that we can properly serialize/deserialize them.
PATHS = [
	Path(),
	Path('c:/users/pyjson_tricks'),
	Path('/home/users/pyjson_tricks'),
	Path('../'),
	Path('..'),
	Path('./'),
	Path('.'),
	Path('test_pathlib.py'),
	Path('/home/users/pyjson_tricks/test_pathlib.py'),
]


def test_path():
	json = dumps(PATHS)
	back = loads(json)
	assert PATHS == back

	for orig, bck in zip(PATHS, back):
		assert orig == bck

	txt = '{"__pathlib__": "."}'
	obj = loads(txt)
	assert obj == Path()

