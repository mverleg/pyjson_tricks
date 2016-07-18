
from .nonp import NoNumpyException, strip_comments, TricksPairHook, \
	ClassInstanceHook, ClassInstanceEncoder, json_date_time_encoder, json_date_time_hook  # keep these 'unused' imports
from . import nonp

try:
	from numpy import ndarray, asarray
except ImportError:
	raise NoNumpyException('Could not load numpy, maybe it is not installed? If you do not want to use numpy encoding '
		'or decoding, you can import the functions from json_tricks.nonp instead, which do not need numpy.')


class NumpyEncoder(ClassInstanceEncoder):
	"""
	JSON encoder for numpy arrays.
	"""
	def default(self, obj, *args, **kwargs):
		"""
		If input object is a ndarray it will be converted into a dict holding
		data type, shape and the data. The object can be restored using json_numpy_obj_hook.
		"""
		if isinstance(obj, ndarray):
			return dict(__ndarray__=obj.tolist(), dtype=str(obj.dtype), shape=obj.shape)
		obj = json_date_time_encoder(obj)
		return super(NumpyEncoder, self).default(obj, *args, **kwargs)


def json_numpy_obj_hook(dct):
	"""
	Replace any numpy arrays previously encoded by NumpyEncoder to their proper
	shape, data type and data.

	:param dct: (dict) json encoded ndarray
	:return: (ndarray) if input was an encoded ndarray
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		return asarray(dct['__ndarray__'], dtype=dct['dtype'])
	return dct


def dumps(obj, sort_keys=None, cls=NumpyEncoder, **jsonkwargs):
	"""
	Like nonp.dumps, but uses NumpyEncoder as default, for handling of numpy arrays.

	:param cls: The json encoder class to use, defaults to NumpyEncoder for handing numpy arrays.
	"""
	return nonp.dumps(obj, sort_keys=sort_keys, cls=cls, **jsonkwargs)


def dump(obj, fp, sort_keys=None, compression=None, cls=NumpyEncoder, **jsonkwargs):
	"""
	Like nonp.dump, but uses NumpyEncoder as default, for handling of numpy arrays.

	:param cls: The json encoder class to use, defaults to NumpyEncoder for handing numpy arrays.
	"""
	return nonp.dump(obj, fp, sort_keys=sort_keys, compression=compression, cls=cls, **jsonkwargs)


def loads(string, decode_cls_instances=True, preserve_order=True, ignore_comments=True, decompression=None,
		obj_pairs_hooks=(json_numpy_obj_hook, json_date_time_hook,), cls_lookup_map=None, allow_duplicates=True,
		**jsonkwargs):
	"""
	Like nonp.loads, but obj_pairs_hooks include json_numpy_obj_hook by default, for handling of numpy arrays.
	"""
	return nonp.loads(string, decode_cls_instances=decode_cls_instances, preserve_order=preserve_order,
		decompression=decompression, obj_pairs_hooks=obj_pairs_hooks, ignore_comments=ignore_comments,
		cls_lookup_map=None, allow_duplicates=allow_duplicates, **jsonkwargs)


def load(fp, decode_cls_instances=True, preserve_order=True, ignore_comments=True, decompression=None,
		obj_pairs_hooks=(json_numpy_obj_hook, json_date_time_hook,), cls_lookup_map=None,
		allow_duplicates=True, **jsonkwargs):
	"""
	Like nonp.load, but obj_pairs_hooks include json_numpy_obj_hook by default, for handling of numpy arrays.
	"""
	return nonp.load(fp, decode_cls_instances=decode_cls_instances, preserve_order=preserve_order,
		ignore_comments=ignore_comments, decompression=decompression, obj_pairs_hooks=obj_pairs_hooks,
		cls_lookup_map=cls_lookup_map, allow_duplicates=allow_duplicates, **jsonkwargs)


