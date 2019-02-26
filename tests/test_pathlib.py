#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This tests timezone-aware date/time objects, which need pytz. Naive date/times should
work with just Python code functionality, and are tested in `nonp`.
"""

from pathlib import Path
from json_tricks import dumps, loads
from json_tricks.utils import is_py3


PATHS = [
		Path(),
		Path(__file__),
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
