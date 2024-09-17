#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from ro_json import dumps, loads

def test_slice():
    original_slice = slice(0, 10, 2)
    json_slice = dumps(original_slice)
    loaded_slice = loads(json_slice)
    assert original_slice == loaded_slice

def test_slice_no_step():
    original_slice = slice(0, 5)
    json_slice = dumps(original_slice)
    loaded_slice = loads(json_slice)
    assert original_slice == loaded_slice
