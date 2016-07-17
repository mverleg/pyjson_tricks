
from datetime import datetime, date, time, timedelta
from logging import warning
from importlib import import_module
from collections import OrderedDict
from gzip import GzipFile
from io import BytesIO
from json import JSONEncoder, loads as json_loads
from re import findall
from sys import version, exc_info


py3 = (version[:2] == '3.')


class NoNumpyException(Exception):
	""" Trying to use numpy features, but numpy cannot be found. """


class DuplicateJsonKeyException(Exception):
	""" Trying to load a json map which contains duplicate keys, but allow_duplicates is False """


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


def strip_comments(string, comment_symbols=frozenset(('#', '//'))):
	"""
	:param string: A string containing json with comments started by comment_symbols.
	:param comment_symbols: Iterable of symbols that start a line comment (default # or //).
	:return: The string with the comments removed.
	"""
	lines = string.splitlines()
	for k in range(len(lines)):
		for symbol in comment_symbols:
			lines[k] = strip_comment_line_with_symbol(lines[k], start=symbol)
	return '\n'.join(lines)


class TricksPairHook(object):
	"""
	Hook that converts json maps to the appropriate python type (dict or OrderedDict)
	and then runs any number of hooks on the individual maps.
	"""
	def __init__(self, ordered=True, obj_pairs_hooks=None, allow_duplicates=True):
		"""
		:param ordered: True if maps should retain their ordering.
		:param obj_pairs_hooks: An iterable of hooks to apply to elements.
		:return:
		"""
		self.map_type = OrderedDict
		if not ordered:
			self.map_type = dict
		self.obj_pairs_hooks = []
		if obj_pairs_hooks:
			self.obj_pairs_hooks = list(obj_pairs_hooks)
		self.allow_duplicates = allow_duplicates

	def __call__(self, pairs):
		if not self.allow_duplicates:
			known = set()
			for key, value in pairs:
				if key in known:
					raise DuplicateJsonKeyException(('Trying to load a json map which contains a duplicate key "{0:}"' +
						' (but allow_duplicates is False)').format(key))
				known.add(key)
		map = self.map_type(pairs)
		for hook in self.obj_pairs_hooks:
			map = hook(map)
		return map


def json_date_time_hook(dct):
	"""
	Return an encoded date, time, datetime or timedelta to it's python representation, including optional timezone.

	:param dct: (dict) json encoded date, time, datetime or timedelta
	:return: (date/time/datetime/timedelta obj) python representation of the above
	"""
	def get_tz(dct):
		if not 'tzinfo' in dct:
			return None
		try:
			import pytz
		except ImportError as err:
			raise ImportError(('Tried to load a json object which has a timezone-aware (date)time. '
				'However, `pytz` could not be imported, so the object could not be loaded. '
				'Error: {0:}').format(str(err)))
		return pytz.timezone(dct['tzinfo'])

	if isinstance(dct, dict):
		if '__date__' in dct:
			return date(year=dct.get('year', 0), month=dct.get('month', 0), day=dct.get('day', 0))
		elif '__time__' in dct:
			tzinfo = get_tz(dct)
			return time(hour=dct.get('hour', 0), minute=dct.get('minute', 0), second=dct.get('second', 0),
				microsecond=dct.get('microsecond', 0), tzinfo=tzinfo)
		elif '__datetime__' in dct:
			tzinfo = get_tz(dct)
			return datetime(year=dct.get('year', 0), month=dct.get('month', 0), day=dct.get('day', 0),
				hour=dct.get('hour', 0), minute=dct.get('minute', 0), second=dct.get('second', 0),
				microsecond=dct.get('microsecond', 0), tzinfo=tzinfo)
		elif '__timedelta__' in dct:
			return timedelta(days=dct.get('days', 0), seconds=dct.get('seconds', 0),
				microseconds=dct.get('microseconds', 0))
	return dct


def json_date_time_encoder(obj):
	"""
	Encode a date, time, datetime or timedelta to a string of a json dictionary, including optional timezone.

	:param obj: date/time/datetime/timedelta obj
	:return: (dict) json primitives representation of date, time, datetime or timedelta
	"""
	if isinstance(obj, datetime):
		dct = OrderedDict([('__datetime__', None), ('year', obj.year), ('month', obj.month),
			('day', obj.day), ('hour', obj.hour), ('minute', obj.minute),
			('second', obj.second), ('microsecond', obj.microsecond)])
		if obj.tzinfo:
			dct['tzinfo'] = obj.tzinfo.zone
	elif isinstance(obj, date):
		dct = OrderedDict([('__date__', None), ('year', obj.year), ('month', obj.month), ('day', obj.day)])
	elif isinstance(obj, time):
		dct = OrderedDict([('__time__', None), ('hour', obj.hour), ('minute', obj.minute),
			('second', obj.second), ('microsecond', obj.microsecond)])
		if obj.tzinfo:
			dct['tzinfo'] = obj.tzinfo.zone
	elif isinstance(obj, timedelta):
		dct = OrderedDict([('__timedelta__', None), ('days', obj.days), ('seconds', obj.seconds),
			('microseconds', obj.microseconds)])
	else:
		return obj
	for key, val in tuple(dct.items()):
		if not key.startswith('__') and not val:
			del dct[key]
	return dct


def json_nonumpy_obj_hook(dct):
	"""
	This hook has no effect except to check if you're trying to decode numpy arrays without support, and give you a useful message.
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		raise NoNumpyException(('Trying to decode dictionary ({0:}) which appears to be a numpy array, but numpy ' +
			'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
			.format(', '.join(dct.keys()[:10])))
	return dct


class ClassInstanceHook(object):
	"""
	This hook tries to convert json encoded by class_instance_encoder back to it's original instance.
	It only works if the environment is the same, e.g. the class is similarly importable and hasn't changed.
	"""
	def __init__(self, cls_lookup_map=None):
		self.cls_lookup_map = cls_lookup_map or {}

	def __call__(self, dct):
		if isinstance(dct, dict) and '__instance_type__' in dct:
			mod, name = dct['__instance_type__']
			attrs = dct['attributes']
			if mod is None:
				try:
					Cls = getattr((__import__('__main__')), name)
				except (ImportError, AttributeError) as err:
					if not name in self.cls_lookup_map:
						raise ImportError(('class {0:s} seems to have been exported from the main file, which means '
							'it has no module/import path set; you need to provide cls_lookup_map which maps names '
							'to classes').format(name))
					Cls = self.cls_lookup_map[name]
			else:
				imp_err = None
				try:
					module = import_module('{0:}'.format(mod, name))
				except ImportError as err:
					imp_err = ('encountered import error "{0:}" while importing "{1:}" to decode a json file; perhaps '
						'it was encoded in a different environment where {1:}.{2:} was available').format(err, mod, name)
				else:
					if not hasattr(module, name):
						imp_err = 'imported "{0:}" but could find "{1:}" inside while decoding a json file (found {2:}'.format(
							module, name, ', '.join(attr for attr in dir(module) if not attr.startswith('_')))
					Cls = getattr(module, name)
				if imp_err:
					if 'name' in self.cls_lookup_map:
						Cls = self.cls_lookup_map[name]
					else:
						raise ImportError(imp_err)
			obj = Cls.__new__(Cls)
			if hasattr(obj, '__json_decode__'):
				obj.__json_decode__(**attrs)
			else:
				obj.__dict__ = dict(attrs)
			return  obj
		return dct


class ClassInstanceEncoder(JSONEncoder):
	"""
	Encodes a class instance to json. Note that it can only be recovered if the environment allows the class to be
	imported in the same way.
	"""
	def __init__(self, obj, encode_cls_instances=True, encode_date_time=True, **kwargs):
		self.encode_cls_instances = encode_cls_instances
		self.encode_date_time = encode_date_time
		super(ClassInstanceEncoder, self).__init__(obj, **kwargs)

	def default(self, obj, *args, **kwargs):
		if isinstance(obj, list) or isinstance(obj, dict):
			return obj
		if hasattr(obj, '__class__') and hasattr(obj, '__dict__'):
			mod = obj.__class__.__module__
			if mod == '__main__':
				mod = None
				warning(('class {0:} seems to have been defined in the main file; unfortunately this means'
					' that it\'s module/import path is unknown, so you might have to provide cls_lookup_map when '
					'decoding').format(obj.__class__))
			name = obj.__class__.__name__
			if hasattr(obj, '__json_encode__'):
				attrs = obj.__json_encode__()
			else:
				attrs = dict(obj.__dict__.items())
			return dict(__instance_type__=(mod, name), attributes=attrs)
		super(ClassInstanceEncoder, self).default(obj, *args, **kwargs)


class NoNumpyEncoder(ClassInstanceEncoder):
	"""
	If the object has a .to_primitives() method, this will be called. Emits a warning for numpy arrays.
	"""
	def default(self, obj, *args, **kwargs):
		if 'ndarray' in str(type(obj)):
			raise NoNumpyException(('Trying to encode {0:} which appears to be a numpy array ({1:}), but numpy ' +
				'support is not enabled. Make sure that numpy is installed and that you import from json_tricks.np.')
				.format(obj, type(obj)))
		print('before:', obj, type(obj))
		obj = json_date_time_encoder(obj)
		print('after:', obj, type(obj))
		return super(NoNumpyEncoder, self).default(obj, *args, **kwargs)


def dumps(obj, encode_cls_instances=True, sort_keys=None, cls=NoNumpyEncoder, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param obj: The Python object to convert.
	:param encode_cls_instances: True to attempt to encode class instances (decoding requires a similar environment).
	:param sort_keys: Keep this False if you want order to be preserved.
	:param cls: The json encoder class to use, defaults to NoNumpyEncoder which gives a warning for numpy arrays.
	:return: The string containing the json-encoded version of obj.

	Other arguments are passed on to json_func. Note that sort_keys should be false if you want to preserve order.

	Use json_tricks.np.dumps instead if you want encoding of numpy arrays.
	"""
	return cls(obj, sort_keys=sort_keys, encode_cls_instances=encode_cls_instances, **jsonkwargs).encode(obj)


def dump(obj, fp, encode_cls_instances=True, sort_keys=None, compression=None, cls=NoNumpyEncoder, **jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param fp: File handle to write to.
	:param compression: The gzip compression level, or None for no compression.

	The other arguments are identical to dumps.

	Use json_tricks.np.dump instead if you want encoding of numpy arrays.
	"""
	string = dumps(obj=obj, encode_cls_instances=encode_cls_instances, sort_keys=sort_keys, cls=cls, **jsonkwargs)
	if compression:
		if compression is True:
			compression = 5
		try:
			with GzipFile(fileobj=fp, mode='wb+', compresslevel=int(compression)) as zh:
				if py3:
					string = bytes(string, 'UTF-8')
				zh.write(string)
		except TypeError as err:
			err.args = (err.args[0] + '. A posible reason is that the file is not opened in binary mode; '
				'be sure to set file mode to something like "wb".',)
			raise
	else:
		fp.write(string)


def loads(string, decode_cls_instances=True, preserve_order=True, ignore_comments=True, decompression=None,
		obj_pairs_hooks=(json_nonumpy_obj_hook, json_date_time_hook,), cls_lookup_map=None, obj_hook=None, allow_duplicates=True,
		**jsonkwargs):
	"""
	Convert a nested data structure to a json string.

	:param string: The string containing a json encoded data structure.
	:param decode_cls_instances: True to attempt to decode class instances (requires the environment to be similar the the encoding one).
	:param preserve_order: Whether to preserve order by using OrderedDicts or not.
	:param ignore_comments: Remove comments (starting with # or //).
	:param decompression: True if gzip decompression should be used, False otherwise.
	:param obj_pairs_hooks: A list of dictionary hooks to apply.
	:param cls_lookup_map: If set to a dict, for example ``globals()``, then classes encoded from __main__ are looked up this dict.
	:param allow_duplicates: If set to False, an error will be raised when loading a json-map that contains duplicate keys.
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
	obj_pairs_hooks = list(obj_pairs_hooks)
	if decode_cls_instances:
		obj_pairs_hooks.append(ClassInstanceHook(cls_lookup_map=cls_lookup_map))
	if obj_hook is not None:
		obj_pairs_hooks.append(obj_hook)
	hook = TricksPairHook(ordered=preserve_order, obj_pairs_hooks=obj_pairs_hooks, allow_duplicates=allow_duplicates)
	return json_loads(string, object_pairs_hook=hook, **jsonkwargs)
	# return json_func(string, object_pairs_hook=hook, **jsonkwargs)


def load(fp, decode_cls_instances=True, preserve_order=True, ignore_comments=True, decompression=None,
		 obj_pairs_hooks=(json_nonumpy_obj_hook, json_date_time_hook,), cls_lookup_map=None,
		 allow_duplicates=True, **jsonkwargs):
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
	return loads(string, decode_cls_instances=decode_cls_instances, preserve_order=preserve_order,
		ignore_comments=ignore_comments, decompression=decompression, obj_pairs_hooks=obj_pairs_hooks,
		cls_lookup_map=cls_lookup_map, allow_duplicates=allow_duplicates, **jsonkwargs)


