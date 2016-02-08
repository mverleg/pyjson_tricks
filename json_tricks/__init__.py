
try:
	# find_module takes just as long as importing, so no optimization possible
	import numpy
except ImportError:
	NUMPY_MODE = False
	from .nonp import dumps, dump, loads, load, strip_comments
else:
	NUMPY_MODE = True
	from .np import dumps, dump, loads, load, strip_comments


__all__ = ['dumps', 'dump', 'loads', 'load', 'strip_comments']


