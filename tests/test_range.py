#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from json_tricks import dumps, loads

def test_range():
    original_range = range(0, 10, 2)
    json_range = dumps(original_range)
    loaded_range = loads(json_range)
    assert original_range == loaded_range

def test_range_no_step():
    original_range = range(0, 5)
    json_range = dumps(original_range)
    loaded_range = loads(json_range)
    assert original_range == loaded_range
