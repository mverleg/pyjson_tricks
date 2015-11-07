
from .nonp import NoNumpyException, strip_hash_comments, TricksPairHook  # keep these 'unused' imports
from json_tricks import nonp
from json import JSONEncoder, loads as json_loads, dumps as json_dumps

try:
	from numpy import ndarray, asarray
except ImportError:
	raise NoNumpyException('Could not load numpy, maybe it is not installed? If you do not want to use numpy encoding or ' +
		'decoding, you can import the functions from json_tricks.nonp instead, which do not need numpy.')


class NumpyEncoder(JSONEncoder):
	"""
	JSON encoder for numpy arrays.
	"""
	def default(self, obj):
		"""
		If input object is a ndarray it will be converted into a dict holding
		data type, shape and the data. The object can be restored using json_numpy_obj_hook.
		"""
		if isinstance(obj, ndarray):
			return dict(__ndarray__ = obj.tolist(), dtype = str(obj.dtype), shape = obj.shape)
		return JSONEncoder(self, obj)


def json_numpy_obj_hook(dct):
	"""
	Replace any numpy arrays previously encoded by NumpyEncoder to their proper
	shape, data type and data.

	:param dct: (dict) json encoded ndarray
	:return: (ndarray) if input was an encoded ndarray
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		return asarray(dct['__ndarray__'], dtype = dct['dtype'])
	return dct


def dumps(obj, preserve_order=True, json_func=json_dumps, cls=NumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Like nonp.dumps, but uses NumpyEncoder as default, for handling of numpy arrays.

	:param cls: The json encoder class to use, defaults to NumpyEncoder for handing numpy arrays.
	"""
	return nonp.dumps(obj, preserve_order=preserve_order, json_func=json_func, cls=cls, sort_keys=sort_keys, **jsonkwargs)


def dump(obj, fp, compression=None, preserve_order=True, json_func=json_dumps, cls=NumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Like nonp.dump, but uses NumpyEncoder as default, for handling of numpy arrays.

	:param cls: The json encoder class to use, defaults to NumpyEncoder for handing numpy arrays.
	"""
	return nonp.dump(obj, fp, compression=compression, preserve_order=preserve_order, json_func=json_func, cls=cls, sort_keys=sort_keys, **jsonkwargs)


def loads(string, preserve_order=True, decompression=None, obj_hooks=(json_numpy_obj_hook,), obj_hook=None, strip_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Like nonp.loads, but obj_hooks include json_numpy_obj_hook by default, for handling of numpy arrays.
	"""
	return nonp.loads(string, preserve_order=preserve_order, decompression=decompression, obj_hooks=obj_hooks, obj_hook=obj_hook, strip_comments=strip_comments, json_func=json_func, **jsonkwargs)


def load(fp, preserve_order=True, decompression=None, obj_hooks=(json_numpy_obj_hook,), obj_hook=None, strip_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Like nonp.load, but obj_hooks include json_numpy_obj_hook by default, for handling of numpy arrays.
	"""
	return nonp.load(fp, preserve_order=preserve_order, decompression=decompression, obj_hooks=obj_hooks, obj_hook=obj_hook, strip_comments=strip_comments, json_func=json_func, **jsonkwargs)


