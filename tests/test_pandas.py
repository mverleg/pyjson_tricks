#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from numpy import linspace, isnan
from pandas import DataFrame, Series
from json_tricks import dumps, loads
from json_tricks.decoders import pandas_hook
from json_tricks.encoders import pandas_encode


COLUMNS = OrderedDict((
	('name', ('Alfa', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliett',)),
	('count', linspace(0, 10, 10, dtype=int)),
	('real', linspace(0, 7.5, 10, dtype=float)),
	('special', (float('NaN'), float('+inf'), float('-inf'), float('+0'), float('-0'), 1, 2, 3, 4, 5)),
	#todo: other types?
))


def test_pandas_dataframe():
	df = DataFrame(COLUMNS, columns=tuple(COLUMNS.keys()))
	txt = dumps(df, extra_obj_encoders=(pandas_encode,), allow_nan=True)
	back = loads(txt, extra_obj_pairs_hooks=(pandas_hook,))
	assert isnan(back.ix[0, -1])
	assert (df.equals(back))
	assert (df.dtypes == back.dtypes).all()


def test_pandas_series():
	for name, col in COLUMNS.items():
		ds = Series(data=col, name=name)
		txt = dumps(ds, extra_obj_encoders=(pandas_encode,), allow_nan=True)
		back = loads(txt, extra_obj_pairs_hooks=(pandas_hook,))
		assert (ds.equals(back))
		assert ds.dtype == back.dtype


