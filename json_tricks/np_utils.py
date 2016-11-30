
from .utils import hashodict
from .nonp import NoNumpyException

try:
	from numpy import generic, complex64, complex128
except ImportError:
	raise NoNumpyException('Could not load numpy, maybe it is not installed?')


def get_scalar_repr(npscalar):
	return hashodict((
		('__ndarray__', npscalar.item()),
		('dtype', str(npscalar.dtype)),
		('shape', ()),
	))


def encode_scalars_inplace(obj):
	"""
	Searches a data structure of lists, tuples and dicts for numpy scalars
	and replaces them by their dictionary representation, which can be loaded
	by json-tricks. This happens in-place (the object is changed, use a copy).
	"""
	if isinstance(obj, (generic, complex64, complex128)):
		return get_scalar_repr(obj)
	if isinstance(obj, dict):
		for key, val in tuple(obj.items()):
			obj[key] = encode_scalars_inplace(val)
		return obj
	if isinstance(obj, list):
		for k, val in enumerate(obj):
			obj[k] = encode_scalars_inplace(val)
		return obj
	if isinstance(obj, (tuple, set)):
		return type(obj)(encode_scalars_inplace(val) for val in obj)
	return obj


