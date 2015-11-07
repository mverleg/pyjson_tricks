
from collections import OrderedDict
from gzip import GzipFile
from io import BytesIO
from json import JSONEncoder, loads as json_loads, dumps as json_dumps
from re import findall
from sys import version, exc_info

py3 = (version[0] == '3')


class NoNumpyException(Exception):
	""" Trying to use numpy features, but numpy cannot be found. """


def strip_comment_line_with_symbol(line, start):
	parts = line.split(start)
	counts = [len(findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part)) for part in parts]
	total = 0
	for nr, count in enumerate(counts):
		total += count
		if total % 2 == 0:
			return start.join(parts[:nr+1]).rstrip()
	else:
		return line.rstrip()


def strip_comments(string, comment_symbols=('#', '//')):
	"""
	:param string: A string containing json with comments started by a # or //.
	:return: The string with the comments removed.
	"""
	lines = string.splitlines()
	for k in range(len(lines)):
		for symbol in comment_symbols:
			lines[k] = strip_comment_line_with_symbol(lines[k], start=symbol)
	return '\n'.join(lines)


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


class NoNumpyEncoder(JSONEncoder):
	"""
	The standard JSONEncoder but with a warning for numpy arrays.
	"""
	def default(self, obj):
		if 'ndarray' in str(type(obj)):
			raise NoNumpyException(('Trying to encode {0:} which appears to be a numpy array ({1:}), but numpy ' +
				'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
				.format(obj, type(obj)))
		return JSONEncoder(self, obj)


def json_nonumpy_obj_hook(dct):
	"""
	This hook has no effect except to check if you're trying to decode numpy arrays without support, and give you a useful message.
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		raise NoNumpyException(('Trying to decode dictionary ({0:}) which appears to be a numpy array, but numpy ' +
			'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
			.format(', '.join(dct.keys()[:10])))
	return dct


def dumps(obj, preserve_order=True, json_func=json_dumps, cls=NoNumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param obj: The Python object to convert.
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param json_func: The underlying dumps function to use (defaults to json.dumps in python >=2.6).
	:param cls: The json encoder class to use, defaults to NoNumpyEncoder which is like JSONEncoder (so doesn't encode numpy arrays).
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func.

	Use json_tricks.np.dumps instead if you want encoding of numpy arrays.
	"""
	assert not (preserve_order and sort_keys), \
		'sort_keys cannot be True if preserve_order is also True as that would bot preserve the order of maps'
	return json_func(obj=obj, cls=cls, sort_keys=sort_keys, **jsonkwargs)


def dump(obj, fp, compression=None, preserve_order=True, json_func=json_dumps, cls=NoNumpyEncoder, sort_keys=None, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle to write to.
	:param compression: The gzip compression level, or None for no compression.

	The other arguments are identical to dumps.

	Use json_tricks.np.dump instead if you want encoding of numpy arrays.
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


def loads(string, preserve_order=True, decompression=None, obj_hooks=(), obj_hook=None, ignore_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param string: The string containing a json encoded data structure.
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param decompression: True if gzip decompression should be used, False otherwise.
	:param obj_hooks: A list of object hooks to apply.
	:param obj_hook: Ab object hook to apply, for compatibility with default json dumps function.
	:param ignore_comments: Remove comments (starting with # or //).
	:param json_func: The underlying dumps function to use (defaults to json.loads in python >=2.6).
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func.

	Use json_tricks.np.loads instead if you want decoding of numpy arrays.
	"""
	if decompression:
		with GzipFile(fileobj=BytesIO(string), mode='rb') as zh:
			string = zh.read()
			if py3:
				string = string.decode('UTF-8')
	if ignore_comments:
		string = strip_comments(string)
	obj_hooks = obj_hooks or []
	if obj_hook is not None:
		obj_hooks.append(obj_hook)
	hook=TricksPairHook(ordered=preserve_order, obj_hooks=obj_hooks)
	return json_func(string, object_pairs_hook=hook, **jsonkwargs)


def load(fp, preserve_order=True, decompression=None, obj_hooks=(), obj_hook=None, ignore_comments=True, json_func=json_loads, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle to load from.

	The other arguments are identical to loads.

	Use json_tricks.np.load instead if you want decoding of numpy arrays.
	"""
	try:
		string = fp.read()
	except UnicodeDecodeError as err:
		raise Exception('There was a problem decoding the file content. A posible reason is that the file is not opened ' +
			'in binary mode; be sure to set file mode to something like "rb".').with_traceback(exc_info()[2])
	return loads(string, preserve_order=preserve_order, decompression=decompression, obj_hooks=obj_hooks, obj_hook=obj_hook, ignore_comments=ignore_comments, json_func=json_func, **jsonkwargs)


