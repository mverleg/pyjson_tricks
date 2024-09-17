import warnings
from base64 import standard_b64encode
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from fractions import Fraction
from functools import wraps
from json import JSONEncoder
from json.encoder import encode_basestring_ascii, encode_basestring, INFINITY
import sys

from .utils import hashodict, get_module_name_from_object, NoEnumException, NoPandasException, \
	NoNumpyException, str_type, JsonTricksDeprecation, gzip_compress, filtered_wrapper, is_py3

def _fallback_wrapper(encoder):
	"""
	This decorator makes an encoder run only if the current object hasn't been changed yet.
	(Changed-ness is checked with is_changed which is based on identity with `id`).
	"""
	@wraps(encoder)
	def fallback_encoder(obj, is_changed, **kwargs):
		if is_changed:
			return obj
		return encoder(obj, is_changed=is_changed, **kwargs)
	return fallback_encoder


def fallback_ignore_unknown(obj, is_changed=None, fallback_value=None):
	"""
	This encoder returns None if the object isn't changed by another encoder and isn't a primitive.
	"""
	if is_changed:
		return obj
	if obj is None or isinstance(obj, (int, float, str_type, bool, list, dict)):
		return obj
	return fallback_value


class TricksEncoder(JSONEncoder):
	"""
	Encoder that runs any number of encoder functions or instances on
	the objects that are being encoded.

	Each encoder should make any appropriate changes and return an object,
	changed or not. This will be passes to the other encoders.
	"""
	def __init__(self, obj_encoders=None, silence_typeerror=False, primitives=False, fallback_encoders=(), properties=None, **json_kwargs):
		"""
		:param obj_encoders: An iterable of functions or encoder instances to try.
		:param silence_typeerror: DEPRECATED - If set to True, ignore the TypeErrors that Encoder instances throw (default False).
		"""
		if silence_typeerror and not getattr(TricksEncoder, '_deprecated_silence_typeerror'):
			TricksEncoder._deprecated_silence_typeerror = True
			sys.stderr.write('TricksEncoder.silence_typeerror is deprecated and may be removed in a future version\n')
		self.obj_encoders = []
		if obj_encoders:
			self.obj_encoders = list(obj_encoders)
		self.obj_encoders.extend(_fallback_wrapper(encoder) for encoder in list(fallback_encoders))
		self.obj_encoders = [filtered_wrapper(enc) for enc in self.obj_encoders]
		self.silence_typeerror = silence_typeerror
		self.properties = properties
		self.primitives = primitives
		super(TricksEncoder, self).__init__(**json_kwargs)

	def default(self, obj, *args, **kwargs):
		"""
		This is the method of JSONEncoders that is called for each object; it calls
		all the encoders with the previous one's output used as input.

		It works for Encoder instances, but they are expected not to throw
		`TypeError` for unrecognized types (the super method does that by default).

		It never calls the `super` method so if there are non-primitive types
		left at the end, you'll get an encoding error.
		"""
		prev_id = id(obj)
		for encoder in self.obj_encoders:
			obj = encoder(obj, primitives=self.primitives, is_changed=id(obj) != prev_id, properties=self.properties)
		if id(obj) == prev_id:
			raise TypeError(('Object of type {0:} could not be encoded by {1:} using encoders [{2:s}]. '
				'You can add an encoders for this type using `extra_obj_encoders`. If you want to \'skip\' this '
				'object, consider using `fallback_encoders` like `str` or `lambda o: None`.').format(
					type(obj), self.__class__.__name__, ', '.join(str(encoder) for encoder in self.obj_encoders)))
		return obj

	def iterencode(self, o, _one_shot=False):
		"""Encode the given object and yield each string
		representation as available.

		For example::

			for chunk in JSONEncoder().iterencode(bigobject):
				mysocket.write(chunk)

		"""
		if self.check_circular:
			markers = {}
		else:
			markers = None
		if self.ensure_ascii:
			_encoder = encode_basestring_ascii
		else:
			_encoder = encode_basestring

		def floatstr(o, allow_nan=self.allow_nan,
				_repr=float.__repr__, _inf=INFINITY, _neginf=-INFINITY):
			# Check for specials.  Note that this type of test is processor
			# and/or platform-specific, so do tests which don't depend on the
			# internals.

			if o != o:
				text = 'NaN'
			elif o == _inf:
				text = 'Infinity'
			elif o == _neginf:
				text = '-Infinity'
			else:
				return _repr(o)

			if not allow_nan:
				raise ValueError(
					"Out of range float values are not JSON compliant: " +
					repr(o))

			return text


		_iterencode = _make_iterencode(
			markers, self.default, _encoder, self.indent, floatstr,
			self.key_separator, self.item_separator, self.sort_keys,
			self.skipkeys, _one_shot)
		return _iterencode(o, 0)


def json_date_time_encode(obj, primitives=False):
	"""
	Encode a date, time, datetime or timedelta to a string of a json dictionary, including optional timezone.

	:param obj: date/time/datetime/timedelta obj
	:return: (dict) json primitives representation of date, time, datetime or timedelta
	"""
	if primitives and isinstance(obj, (date, time, datetime)):
		return obj.isoformat()
	if isinstance(obj, datetime):
		dct = hashodict([('__datetime__', None), ('year', obj.year), ('month', obj.month),
			('day', obj.day), ('hour', obj.hour), ('minute', obj.minute),
			('second', obj.second), ('microsecond', obj.microsecond)])
		if obj.tzinfo:
			if hasattr(obj.tzinfo, 'zone'):
				dct['tzinfo'] = obj.tzinfo.zone
			else:
				dct['tzinfo'] = obj.tzinfo.tzname(None)
			dct['is_dst'] = bool(obj.dst())
	elif isinstance(obj, date):
		dct = hashodict([('__date__', None), ('year', obj.year), ('month', obj.month), ('day', obj.day)])
	elif isinstance(obj, time):
		dct = hashodict([('__time__', None), ('hour', obj.hour), ('minute', obj.minute),
			('second', obj.second), ('microsecond', obj.microsecond)])
		if obj.tzinfo:
			if hasattr(obj.tzinfo, 'zone'):
				dct['tzinfo'] = obj.tzinfo.zone
			else:
				dct['tzinfo'] = obj.tzinfo.tzname(None)
	elif isinstance(obj, timedelta):
		if primitives:
			return obj.total_seconds()
		else:
			dct = hashodict([('__timedelta__', None), ('days', obj.days), ('seconds', obj.seconds),
				('microseconds', obj.microseconds)])
	else:
		return obj
	for key, val in tuple(dct.items()):
		if not key.startswith('__') and not key == 'is_dst' and not val:
			del dct[key]
	return dct


def enum_instance_encode(obj, primitives=False, with_enum_value=False):
	"""Encodes an enum instance to json. Note that it can only be recovered if the environment allows the enum to be
	imported in the same way.
	:param primitives: If true, encode the enum values as primitive (more readable, but cannot be restored automatically).
	:param with_enum_value: If true, the value of the enum is also exported (it is not used during import, as it should be constant).
	"""
	from enum import Enum
	if not isinstance(obj, Enum):
		return obj
	if primitives:
		return {obj.name: obj.value}
	mod = get_module_name_from_object(obj)
	representation = dict(
		__enum__=dict(
			# Don't use __instance_type__ here since enums members cannot be created with __new__
			# Ie we can't rely on class deserialization to read them.
			__enum_instance_type__=[mod, type(obj).__name__],
			name=obj.name,
		),
	)
	if with_enum_value:
		representation['__enum__']['value'] = obj.value
	return representation


def noenum_instance_encode(obj, primitives=False):
	if type(obj.__class__).__name__ == 'EnumMeta':
		raise NoEnumException(('Trying to encode an object of type {0:} which appears to be '
			'an enum, but enum support is not enabled, perhaps it is not installed.').format(type(obj)))
	return obj


def class_instance_encode(obj, primitives=False):
	"""
	Encodes a class instance to json. Note that it can only be recovered if the environment allows the class to be
	imported in the same way.
	"""
	if isinstance(obj, list) or isinstance(obj, dict):
		return obj
	if hasattr(obj, '__class__') and (hasattr(obj, '__dict__') or hasattr(obj, '__slots__')):
		if not hasattr(obj, '__new__'):
			raise TypeError('class "{0:s}" does not have a __new__ method; '.format(obj.__class__) +
				('perhaps it is an old-style class not derived from `object`; add `object` as a base class to encode it.'
					if (sys.version[:2] == '2.') else 'this should not happen in Python3'))
		if type(obj) == type(lambda: 0):
			raise TypeError('instance "{0:}" of class "{1:}" cannot be encoded because it appears to be a lambda or function.'
				.format(obj, obj.__class__))
		try:
			obj.__new__(obj.__class__)
		except TypeError:
			raise TypeError(('instance "{0:}" of class "{1:}" cannot be encoded, perhaps because it\'s __new__ method '
				'cannot be called because it requires extra parameters').format(obj, obj.__class__))
		mod = get_module_name_from_object(obj)
		if mod == 'threading':
			# In Python2, threading objects get serialized, which is probably unsafe
			return obj
		name = obj.__class__.__name__
		if hasattr(obj, '__json_encode__'):
			attrs = obj.__json_encode__()
			if primitives:
				return attrs
			else:
				return hashodict((('__instance_type__', (mod, name)), ('attributes', attrs)))
		dct = hashodict([('__instance_type__',(mod, name))])
		if hasattr(obj, '__slots__'):
			slots = obj.__slots__
			if isinstance(slots, str):
				slots = [slots]
			dct['slots'] = hashodict([])
			for s in slots:
				if s == '__dict__':
					continue
				if s == '__weakref__':
					continue
				dct['slots'][s] = getattr(obj, s)
		if hasattr(obj, '__dict__'):
			dct['attributes'] = hashodict(obj.__dict__)
		if primitives:
			attrs = dct.get('attributes',{})
			attrs.update(dct.get('slots',{}))
			return attrs
		else:
			return dct
	return obj


def json_complex_encode(obj, primitives=False):
	"""
	Encode a complex number as a json dictionary of its real and imaginary part.

	:param obj: complex number, e.g. `2+1j`
	:return: (dict) json primitives representation of `obj`
	"""
	if isinstance(obj, complex):
		if primitives:
			return [obj.real, obj.imag]
		else:
			return hashodict(__complex__=[obj.real, obj.imag])
	return obj


def bytes_encode(obj, primitives=False):
	"""
	Encode bytes as one of these:

	* A utf8-string with special `__bytes_utf8__` marking, if the bytes are valid utf8 and primitives is False.
	* A base64 encoded string of the bytes with special `__bytes_b64__` marking, if the bytes are not utf8, or if primitives is True.

	:param obj: any object, which will be transformed if it is of type bytes
	:return: (dict) json primitives representation of `obj`
	"""
	if isinstance(obj, bytes):
		if not is_py3:
			return obj
		if primitives:
			return hashodict(__bytes_b64__=standard_b64encode(obj).decode('ascii'))
		else:
			try:
				return hashodict(__bytes_utf8__=obj.decode('utf-8'))
			except UnicodeDecodeError:
				return hashodict(__bytes_b64__=standard_b64encode(obj).decode('ascii'))
	return obj


def numeric_types_encode(obj, primitives=False):
	"""
	Encode Decimal and Fraction.

	:param primitives: Encode decimals and fractions as standard floats. You may lose precision. If you do this, you may need to enable `allow_nan` (decimals always allow NaNs but floats do not).
	"""
	if isinstance(obj, Decimal):
		if primitives:
			return float(obj)
		else:
			return {
				'__decimal__': str(obj.canonical()),
			}
	if isinstance(obj, Fraction):
		if primitives:
			return float(obj)
		else:
			return hashodict((
				('__fraction__', True),
				('numerator', obj.numerator),
				('denominator', obj.denominator),
			))
	return obj


def pathlib_encode(obj, primitives=False):
	from pathlib import Path
	if not isinstance(obj, Path):
		return obj

	if primitives:
		return str(obj)

	return {'__pathlib__': str(obj)}

def slice_encode(obj, primitives=False):
	if not isinstance(obj, slice):
		return obj

	if primitives:
		return [obj.start, obj.stop, obj.step]
	else:
		return hashodict((
			('__slice__', True),
			('start', obj.start),
			('stop', obj.stop),
			('step', obj.step),
		))

def range_encode(obj, primitives=False):
	if not isinstance(obj, range):
		return obj

	if primitives:
		return [obj.start, obj.stop, obj.step]
	else:
		return hashodict((
			('__range__', True),
			('start', obj.start),
			('stop', obj.stop),
			('step', obj.step),
		))

class ClassInstanceEncoder(JSONEncoder):
	"""
	See `class_instance_encoder`.
	"""
	# Not covered in tests since `class_instance_encode` is recommended way.
	def __init__(self, obj, encode_cls_instances=True, **kwargs):
		self.encode_cls_instances = encode_cls_instances
		super(ClassInstanceEncoder, self).__init__(obj, **kwargs)

	def default(self, obj, *args, **kwargs):
		if self.encode_cls_instances:
			obj = class_instance_encode(obj)
		return super(ClassInstanceEncoder, self).default(obj, *args, **kwargs)


def json_set_encode(obj, primitives=False):
	"""
	Encode python sets as dictionary with key __set__ and a list of the values.

	Try to sort the set to get a consistent json representation, use arbitrary order if the data is not ordinal.
	"""
	if isinstance(obj, set):
		try:
			repr = sorted(obj)
		except Exception:
			repr = list(obj)
		if primitives:
			return repr
		else:
			return hashodict(__set__=repr)
	return obj


def pandas_encode(obj, primitives=False):
	from pandas import DataFrame, Series
	if isinstance(obj, DataFrame):
		repr = hashodict()
		if not primitives:
			repr['__pandas_dataframe__'] = hashodict((
				('column_order', tuple(obj.columns.values)),
				('types', tuple(str(dt) for dt in obj.dtypes)),
			))
		repr['index'] = tuple(obj.index.values)
		for k, name in enumerate(obj.columns.values):
			repr[name] = tuple(obj.iloc[:, k].values)
		return repr
	if isinstance(obj, Series):
		repr = hashodict()
		if not primitives:
			repr['__pandas_series__'] = hashodict((
				('name', str(obj.name)),
				('type', str(obj.dtype)),
			))
		repr['index'] = tuple(obj.index.values)
		repr['data'] = tuple(obj.values)
		return repr
	return obj


def nopandas_encode(obj):
	if ('DataFrame' in getattr(obj.__class__, '__name__', '') or 'Series' in getattr(obj.__class__, '__name__', '')) \
			and 'pandas.' in getattr(obj.__class__, '__module__', ''):
		raise NoPandasException(('Trying to encode an object of type {0:} which appears to be '
			'a numpy array, but numpy support is not enabled, perhaps it is not installed.').format(type(obj)))
	return obj


def numpy_encode(obj, primitives=False, properties=None):
	"""
	Encodes numpy `ndarray`s as lists with meta data.

	Encodes numpy scalar types as Python equivalents. Special encoding is not possible,
	because int64 (in py2) and float64 (in py2 and py3) are subclasses of primitives,
	which never reach the encoder.

	:param primitives: If True, arrays are serialized as (nested) lists without meta info.
	"""
	from numpy import ndarray, generic, datetime64

	scalar_types = (generic, datetime64)

	if isinstance(obj, ndarray):
		if primitives:
			return obj.tolist()
		else:
			properties = properties or {}
			use_compact = properties.get('ndarray_compact', None)
			store_endianness = properties.get('ndarray_store_byteorder', None)
			assert store_endianness in [None, 'little', 'big', 'suppress'] ,\
				'property ndarray_store_byteorder should be \'little\', \'big\' or \'suppress\' if provided'
			json_compression = bool(properties.get('compression', False))
			if use_compact is None and json_compression and not getattr(numpy_encode, '_warned_compact', False):
				numpy_encode._warned_compact = True
				warnings.warn('storing ndarray in text format while compression in enabled; in the next major version '
					'of json_tricks, the default when using compression will change to compact mode; to already use '
					'that smaller format, pass `properties={"ndarray_compact": True}` to ro_json.dump; '
					'to silence this warning, pass `properties={"ndarray_compact": False}`; '
					'see issue https://github.com/mverleg/pyjson_tricks/issues/73', JsonTricksDeprecation)
			# Property 'use_compact' may also be an integer, in which case it's the number of
			# elements from which compact storage is used.
			if isinstance(use_compact, int) and not isinstance(use_compact, bool):
				use_compact = obj.size >= use_compact
			if use_compact:
				# If the overall json file is compressed, then don't compress the array.
				data_json = _ndarray_to_bin_str(obj, do_compress=not json_compression, store_endianness=store_endianness)
			else:
				data_json = obj.tolist()
			dct = hashodict((
				('__ndarray__', data_json),
				('dtype', str(obj.dtype)),
				('shape', obj.shape),
				('0dim', obj.ndim == 0),
			))
			if len(obj.shape) > 1:
				dct['Corder'] = obj.flags['C_CONTIGUOUS']
			if use_compact and store_endianness != 'suppress':
				dct['endian'] = store_endianness or sys.byteorder
			return dct
	elif isinstance(obj, scalar_types):
		return hashodict((
			('__ndarray__', obj.item()),
			('dtype', str(obj.dtype)),
			('0dim', False),
		))
	return obj


def _ndarray_to_bin_str(array, do_compress, store_endianness):
	"""
	From ndarray to base64 encoded, gzipped binary data.
	"""
	from base64 import standard_b64encode
	assert array.flags['C_CONTIGUOUS'], 'only C memory order is (currently) supported for compact ndarray format'

	original_size = array.size * array.itemsize
	header = 'b64:'
	if store_endianness in ['little', 'big'] and store_endianness != sys.byteorder:
		array = array.byteswap(inplace=False)
	data = array.data
	if do_compress:
		small = gzip_compress(data, compresslevel=9)
		if len(small) < 0.9 * original_size and len(small) < original_size - 8:
			header = 'b64.gz:'
			data = small
	data = standard_b64encode(data)
	return header + data.decode('ascii')


class NumpyEncoder(ClassInstanceEncoder):
	"""
	JSON encoder for numpy arrays.
	"""
	SHOW_SCALAR_WARNING = True	# show a warning that numpy scalar serialization is experimental

	def default(self, obj, *args, **kwargs):
		"""
		If input object is a ndarray it will be converted into a dict holding
		data type, shape and the data. The object can be restored using json_numpy_obj_hook.
		"""
		warnings.warn('`NumpyEncoder` is deprecated, use `numpy_encode`', JsonTricksDeprecation)
		obj = numpy_encode(obj)
		return super(NumpyEncoder, self).default(obj, *args, **kwargs)


def nonumpy_encode(obj):
	"""
	Raises an error for numpy arrays.
	"""
	if 'ndarray' in getattr(obj.__class__, '__name__', '') and 'numpy.' in getattr(obj.__class__, '__module__', ''):
		raise NoNumpyException(('Trying to encode an object of type {0:} which appears to be '
			'a pandas data stucture, but pandas support is not enabled, perhaps it is not installed.').format(type(obj)))
	return obj


class NoNumpyEncoder(JSONEncoder):
	"""
	See `nonumpy_encode`.
	"""
	def default(self, obj, *args, **kwargs):
		warnings.warn('`NoNumpyEncoder` is deprecated, use `nonumpy_encode`', JsonTricksDeprecation)
		obj = nonumpy_encode(obj)
		return super(NoNumpyEncoder, self).default(obj, *args, **kwargs)

def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
		_key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot,
		## HACK: hand-optimized bytecode; turn globals into locals
		ValueError=ValueError,
		dict=dict,
		float=float,
		id=id,
		int=int,
		isinstance=isinstance,
		list=list,
		str=str,
		tuple=tuple,
		_intstr=int.__repr__,
	):

	try:
		import numpy
		def isfloatinstance(obj):
			return isinstance(obj, float) and not isinstance(obj, numpy.number)
	except ImportError:
		def isfloatinstance(obj):
			return isinstance(obj, float)

	if _indent is not None and not isinstance(_indent, str):
		_indent = ' ' * _indent

	def _iterencode_list(lst, _current_indent_level):
		if not lst:
			yield '[]'
			return
		if markers is not None:
			markerid = id(lst)
			if markerid in markers:
				raise ValueError("Circular reference detected")
			markers[markerid] = lst
		buf = '['
		if _indent is not None:
			_current_indent_level += 1
			newline_indent = '\n' + _indent * _current_indent_level
			separator = _item_separator + newline_indent
			buf += newline_indent
		else:
			newline_indent = None
			separator = _item_separator
		first = True
		for value in lst:
			if first:
				first = False
			else:
				buf = separator
			if isinstance(value, str):
				yield buf + _encoder(value)
			elif value is None:
				yield buf + 'null'
			elif value is True:
				yield buf + 'true'
			elif value is False:
				yield buf + 'false'
			elif isinstance(value, int):
				# Subclasses of int/float may override __repr__, but we still
				# want to encode them as integers/floats in JSON. One example
				# within the standard library is IntEnum.
				yield buf + _intstr(value)
			elif isfloatinstance(value):
				# see comment above for int
				yield buf + _floatstr(value)
			else:
				yield buf
				if isinstance(value, (list, tuple)):
					chunks = _iterencode_list(value, _current_indent_level)
				elif isinstance(value, dict):
					chunks = _iterencode_dict(value, _current_indent_level)
				else:
					chunks = _iterencode(value, _current_indent_level)
				yield from chunks
		if newline_indent is not None:
			_current_indent_level -= 1
			yield '\n' + _indent * _current_indent_level
		yield ']'
		if markers is not None:
			del markers[markerid]

	def _iterencode_dict(dct, _current_indent_level):
		if not dct:
			yield '{}'
			return
		if markers is not None:
			markerid = id(dct)
			if markerid in markers:
				raise ValueError("Circular reference detected")
			markers[markerid] = dct
		yield '{'
		if _indent is not None:
			_current_indent_level += 1
			newline_indent = '\n' + _indent * _current_indent_level
			item_separator = _item_separator + newline_indent
			yield newline_indent
		else:
			newline_indent = None
			item_separator = _item_separator
		first = True
		if _sort_keys:
			items = sorted(dct.items())
		else:
			items = dct.items()
		for key, value in items:
			if isinstance(key, str):
				pass
			# JavaScript is weakly typed for these, so it makes sense to
			# also allow them.	Many encoders seem to do something like this.
			elif isinstance(key, float):
				# see comment for int/float in _make_iterencode
				key = _floatstr(key)
			elif key is True:
				key = 'true'
			elif key is False:
				key = 'false'
			elif key is None:
				key = 'null'
			elif isinstance(key, int):
				# see comment for int/float in _make_iterencode
				key = _intstr(key)
			elif _skipkeys:
				continue
			else:
				raise TypeError(f'keys must be str, int, float, bool or None, '
								f'not {key.__class__.__name__}')
			if first:
				first = False
			else:
				yield item_separator
			yield _encoder(key)
			yield _key_separator
			if isinstance(value, str):
				yield _encoder(value)
			elif value is None:
				yield 'null'
			elif value is True:
				yield 'true'
			elif value is False:
				yield 'false'
			elif isinstance(value, int):
				# see comment for int/float in _make_iterencode
				yield _intstr(value)
			elif isfloatinstance(value):
				# see comment for int/float in _make_iterencode
				yield _floatstr(value)
			else:
				if isinstance(value, (list, tuple)):
					chunks = _iterencode_list(value, _current_indent_level)
				elif isinstance(value, dict):
					chunks = _iterencode_dict(value, _current_indent_level)
				else:
					chunks = _iterencode(value, _current_indent_level)
				yield from chunks
		if newline_indent is not None:
			_current_indent_level -= 1
			yield '\n' + _indent * _current_indent_level
		yield '}'
		if markers is not None:
			del markers[markerid]

	def _iterencode(o, _current_indent_level):
		if isinstance(o, str):
			yield _encoder(o)
		elif o is None:
			yield 'null'
		elif o is True:
			yield 'true'
		elif o is False:
			yield 'false'
		elif isinstance(o, int):
			# see comment for int/float in _make_iterencode
			yield _intstr(o)
		elif isfloatinstance(o):
			# see comment for int/float in _make_iterencode
			yield _floatstr(o)
		elif isinstance(o, (list, tuple)):
			yield from _iterencode_list(o, _current_indent_level)
		elif isinstance(o, dict):
			yield from _iterencode_dict(o, _current_indent_level)
		else:
			if markers is not None:
				markerid = id(o)
				if markerid in markers:
					raise ValueError("Circular reference detected")
				markers[markerid] = o
			o = _default(o)
			yield from _iterencode(o, _current_indent_level)
			if markers is not None:
				del markers[markerid]
	return _iterencode
