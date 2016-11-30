
from datetime import datetime, date, time, timedelta
from importlib import import_module
from collections import OrderedDict


class DuplicateJsonKeyException(Exception):
	""" Trying to load a json map which contains duplicate keys, but allow_duplicates is False """


class TricksPairHook(object):
	"""
	Hook that converts json maps to the appropriate python type (dict or OrderedDict)
	and then runs any number of hooks on the individual maps.
	"""
	def __init__(self, ordered=True, obj_pairs_hooks=None, allow_duplicates=True):
		"""
		:param ordered: True if maps should retain their ordering.
		:param obj_pairs_hooks: An iterable of hooks to apply to elements.
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
					raise DuplicateJsonKeyException(('Trying to load a json map which contains a' +
						' duplicate key "{0:}" (but allow_duplicates is False)').format(key))
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


def json_complex_hook(dct):
	"""
	Return an encoded complex number to it's python representation.

	:param dct: (dict) json encoded complex number (__complex__)
	:return: python complex number
	"""
	if isinstance(dct, dict):
		if '__complex__' in dct:
			parts = dct['__complex__']
			assert len(parts) == 2
			return parts[0] + parts[1] * 1j
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
			try:
				obj = Cls.__new__(Cls)
			except TypeError:
				raise TypeError(('problem while decoding instance of "{0:s}"; this instance has a special '
					'__new__ method and can\'t be restored').format(name))
			if hasattr(obj, '__json_decode__'):
				obj.__json_decode__(**attrs)
			else:
				obj.__dict__ = dict(attrs)
			return  obj
		return dct


def json_set_hook(dct):
	"""
	Return an encoded set to it's python representation.
	"""
	if isinstance(dct, dict):
		if '__set__' in dct:
			return set((tuple(item) if isinstance(item, list) else item) for item in dct['__set__'])
	return dct


