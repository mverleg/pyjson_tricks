
from gzip import GzipFile
from io import BytesIO
from json import loads as json_loads
from os import fsync
from sys import exc_info, version
from .comment import strip_comment_line_with_symbol, strip_comments  # keep 'unused' imports
from .encoders import TricksEncoder, json_date_time_encode, class_instance_encode, ClassInstanceEncoder, \
	json_complex_encode, json_set_encode  # keep 'unused' imports
from .decoders import DuplicateJsonKeyException, TricksPairHook, json_date_time_hook, ClassInstanceHook, \
	json_complex_hook, json_set_hook  # keep 'unused' imports
from json import JSONEncoder


is_py3 = (version[:2] == '3.')
str_type = str if is_py3 else basestring
ENCODING = 'UTF-8'


class NoNumpyException(Exception):
		""" Trying to use numpy features, but numpy cannot be found. """


def nonumpy_encode(obj):
	"""
	Emits a warning for numpy arrays, no other effect.
	"""
	if 'ndarray' in str(type(obj)):
		raise NoNumpyException(('Trying to encode {0:} which appears to be a numpy array ({1:}), but numpy ' +
			'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
			.format(obj, type(obj)))
	return obj


class NoNumpyEncoder(JSONEncoder):
	"""
	See `nonumpy_encoder`.
	"""
	def default(self, obj, *args, **kwargs):
		obj = nonumpy_encode(obj)
		return super(NoNumpyEncoder, self).default(obj, *args, **kwargs)


def json_nonumpy_obj_hook(dct):
	"""
	This hook has no effect except to check if you're trying to decode numpy arrays without support, and give you a useful message.
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		raise NoNumpyException(('Trying to decode dictionary ({0:}) which appears to be a numpy array, but numpy ' +
			'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
			.format(', '.join(dct.keys()[:10])))
	return dct


_cih_instance = ClassInstanceHook()
DEFAULT_ENCODERS = (json_date_time_encode, class_instance_encode, json_complex_encode, json_set_encode,)
DEFAULT_NONP_ENCODERS = DEFAULT_ENCODERS + (nonumpy_encode,)
DEFAULT_HOOKS = (json_date_time_hook, _cih_instance, json_complex_hook, json_set_hook,)
DEFAULT_NONP_HOOKS = (json_nonumpy_obj_hook,) + DEFAULT_HOOKS


def dumps(obj, sort_keys=None, cls=TricksEncoder, obj_encoders=DEFAULT_NONP_ENCODERS, extra_obj_encoders=(),
		compression=None, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param obj: The Python object to convert.
	:param sort_keys: Keep this False if you want order to be preserved.
	:param cls: The json encoder class to use, defaults to NoNumpyEncoder which gives a warning for numpy arrays.
	:param obj_encoders: Iterable of encoders to use to convert arbitrary objects into json-able promitives.
	:param extra_obj_encoders: Like `obj_encoders` but on top of them: use this to add encoders without replacing defaults. Since v3.5 these happen before default encoders.
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to `cls`. Note that `sort_keys` should be false if you want to preserve order.

	Use `json_tricks.np.dumps` instead if you want encoding of numpy arrays.
	"""
	encoders = tuple(extra_obj_encoders) + tuple(obj_encoders)
	string = cls(sort_keys=sort_keys, obj_encoders=encoders, **jsonkwargs).encode(obj)
	if not compression:
		return string
	if compression is True:
		compression = 5
	if is_py3:
		string = bytes(string, encoding=ENCODING)
	sh = BytesIO()
	with GzipFile(mode='wb', fileobj=sh, compresslevel=compression) as zh:
		zh.write(string)
	gzstring = sh.getvalue()
	return gzstring


def dump(obj, fp, sort_keys=None, cls=TricksEncoder, obj_encoders=DEFAULT_NONP_ENCODERS, extra_obj_encoders=(),
		compression=None, force_flush=False, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle or path to write to.
	:param compression: The gzip compression level, or None for no compression.
	:param force_flush: If True, flush the file handle used, when possibly also in the operating system (default False).
	
	The other arguments are identical to `dumps`.

	Use `json_tricks.np.dump` instead if you want encoding of numpy arrays.
	"""
	string = dumps(obj, sort_keys=sort_keys, cls=cls, obj_encoders=obj_encoders, extra_obj_encoders=extra_obj_encoders,
		compression=compression, **jsonkwargs)
	if isinstance(fp, str_type):
		fh = open(fp, 'wb+')
	else:
		fh = fp
	try:
		try:
			fh.write(string)
		except TypeError as err:
			err.args = (err.args[0] + '. A possible reason is that the file is not opened in binary mode; '
				'be sure to set file mode to something like "wb".',)
			raise
	finally:
		if force_flush:
			fh.flush()
			try:
				if fh.fileno() is not None:
					fsync(fh.fileno())
			except (ValueError,):
				pass
		if isinstance(fp, str_type):
			fh.close()
	return string


def loads(string, preserve_order=True, ignore_comments=True, decompression=None, obj_pairs_hooks=DEFAULT_NONP_HOOKS,
		extra_obj_pairs_hooks=(), cls_lookup_map=None, allow_duplicates=True, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param string: The string containing a json encoded data structure.
	:param decode_cls_instances: True to attempt to decode class instances (requires the environment to be similar the the encoding one).
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param ignore_comments: Remove comments (starting with # or //).
	:param decompression: True to use gzip decompression, False to use raw data, None to automatically determine (default).
	:param obj_pairs_hooks: A list of dictionary hooks to apply.
	:param extra_obj_pairs_hooks: Like `obj_pairs_hooks` but on top of them: use this to add hooks without replacing defaults. Since v3.5 these happen before default hooks.
	:param cls_lookup_map: If set to a dict, for example ``globals()``, then classes encoded from __main__ are looked up this dict.
	:param allow_duplicates: If set to False, an error will be raised when loading a json-map that contains duplicate keys.
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func.

	Use json_tricks.np.loads instead if you want decoding of numpy arrays.
	"""
	if decompression is None:
		decompression = string[:2] == b'\x1f\x8b'
	if decompression:
		with GzipFile(fileobj=BytesIO(string), mode='rb') as zh:
			string = zh.read()
			if is_py3:
				string = str(string, encoding=ENCODING)
	if ignore_comments:
		string = strip_comments(string)
	obj_pairs_hooks = tuple(obj_pairs_hooks)
	_cih_instance.cls_lookup_map = cls_lookup_map or {}
	hooks = tuple(extra_obj_pairs_hooks) + obj_pairs_hooks
	hook = TricksPairHook(ordered=preserve_order, obj_pairs_hooks=hooks, allow_duplicates=allow_duplicates)
	return json_loads(string, object_pairs_hook=hook, **jsonkwargs)


def load(fp, preserve_order=True, ignore_comments=True, decompression=None, obj_pairs_hooks=DEFAULT_NONP_HOOKS,
		extra_obj_pairs_hooks=(), cls_lookup_map=None, allow_duplicates=True, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle or path to load from.

	The other arguments are identical to loads.

	Use json_tricks.np.load instead if you want decoding of numpy arrays.
	"""
	try:
		if isinstance(fp, str_type):
			with open(fp, 'rb') as fh:
				string = fh.read()
		else:
			string = fp.read()
	except UnicodeDecodeError as err:
		raise Exception('There was a problem decoding the file content. A possible reason is that the file is not ' +
			'opened  in binary mode; be sure to set file mode to something like "rb".').with_traceback(exc_info()[2])
	return loads(string, preserve_order=preserve_order, ignore_comments=ignore_comments, decompression=decompression,
		obj_pairs_hooks=obj_pairs_hooks, extra_obj_pairs_hooks=extra_obj_pairs_hooks, cls_lookup_map=cls_lookup_map,
		allow_duplicates=allow_duplicates, **jsonkwargs)


