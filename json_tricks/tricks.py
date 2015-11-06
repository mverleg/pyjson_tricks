
from collections import OrderedDict
from gzip import GzipFile
from io import BytesIO
from numpy import ndarray, asarray
from json import JSONEncoder, loads as json_loads, dumps as json_dumps
from re import findall
from sys import version, exc_info

py3 = (version[0] == '3')


def strip_hash_comments(string):
	"""
	:param string: A string containing json with comments started by a #.
	:return: The string with the comments removed.
	"""
	lines = string.splitlines()
	for k, line in enumerate(lines):
		parts = line.split('#')
		counts = [len(findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part)) for part in parts]
		total = 0
		for nr, count in enumerate(counts):
			total += count
			if total % 2 == 0:
				lines[k] = '#'.join(parts[:nr+1]).rstrip()
				break
		else:
			lines[k] = line.rstrip()
	return '\n'.join(lines)


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
		return asarray(dct['__ndarray__'], dtype = dct['dtype'])#.reshape(dct['shape'])
	return dct


class TricksPairHook:
	"""
	Hook that converts json maps to the appropriate python type (dict or OrderedDict)
	and then runs any number of hooks on the individual maps.
	"""
	def __init__(self, ordered=True, obj_hooks=None):
		"""
		:param ordered: True if maps should retain their ordering.
		:param obj_hooks: An iterable of hooks to apply to elements.
		:return:
		"""
		self.map_type = OrderedDict
		if not ordered:
			self.map_type = dict
		self.obj_hooks = []
		if obj_hooks:
			self.obj_hooks = list(obj_hooks)

	def __call__(self, pairs):
		map = self.map_type(pairs)
		for hook in self.obj_hooks:
			map = hook(map)
		return map


def dumps(obj, preserve_order=True, json_func=json_dumps, cls=NumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param obj: The Python object to convert.
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param json_func: The underlying dumps function to use (defaults to json.dumps in python >=2.6).
	:param cls: The json encoder class to use, defaults to NumpyEncoder for handing numpy arrays.
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func.
	"""
	assert not (preserve_order and sort_keys), \
		'sort_keys cannot be True if preserve_order is also True as that would bot preserve the order of maps'
	return json_func(obj=obj, cls=cls, sort_keys=sort_keys, **jsonkwargs)


def dump(obj, fp, compression=None, preserve_order=True, json_func=json_dumps, cls=NumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle to write to.
	:param compression: The gzip compression level, or None for no compression.

	The other arguments are identical to dumps.
	"""
	string = dumps(obj=obj, preserve_order=preserve_order, json_func=json_func, cls=cls, sort_keys=sort_keys, **jsonkwargs)
	if compression:
		try:
			with GzipFile(fileobj=fp, mode='wb+', compresslevel=int(compression)) as zh:
				if py3:
					string = bytes(string, 'UTF-8')
				zh.write(string)
		except TypeError as err:
			err.args = (err.args[0] + '. A posible reason is that the file is not opened in binary mode; be sure to set file mode to something like "wb".',)
			raise
	else:
		fp.write(string)


def loads(string, preserve_order=True, decompression=None, obj_hooks=(json_numpy_obj_hook,), obj_hook=None, strip_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param string: The string containing a json encoded data structure.
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param decompression: True if gzip decompression should be used, False otherwise.
	:param obj_hooks: A list of object hooks to apply.
	:param obj_hook: Ab object hook to apply, for compatibility with default json dumps function.
	:param strip_comments: Remove lines starting with a # sign.
	:param json_func: The underlying dumps function to use (defaults to json.loads in python >=2.6).
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func.
	"""
	if decompression:
		with GzipFile(fileobj=BytesIO(string), mode='rb') as zh:
			string = zh.read()
			if py3:
				string = string.decode('UTF-8')
	if strip_comments:
		string = strip_hash_comments(string)
	obj_hooks = obj_hooks or []
	if obj_hook is not None:
		obj_hooks.append(obj_hook)
	hook=TricksPairHook(ordered=preserve_order, obj_hooks=obj_hooks)
	return json_func(string, object_pairs_hook=hook, **jsonkwargs)


def load(fp, preserve_order=True, decompression=None, obj_hooks=(json_numpy_obj_hook,), obj_hook=None, strip_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle to load from.

	The other arguments are identical to loads.
	"""
	try:
		string = fp.read()
	except UnicodeDecodeError as err:
		raise Exception('There was a problem decoding the file content. A posible reason is that the file is not opened ' +
		    'in binary mode; be sure to set file mode to something like "rb".').with_traceback(exc_info()[2])
	return loads(string, preserve_order=preserve_order, decompression=decompression, obj_hooks=obj_hooks, obj_hook=obj_hook, strip_comments=strip_comments, json_func=json_func, **jsonkwargs)


