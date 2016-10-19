
from datetime import datetime, date, time, timedelta
from logging import warning
from collections import OrderedDict
from json import JSONEncoder


class TricksEncoder(JSONEncoder):
	"""
	Encoder that runs any number of encoder functions or instances on
	the objects that are being encoded.

	Each encoder should make any appropriate changes and return an object,
	changed or not. This will be passes to the other encoders.
	"""
	def __init__(self, obj_encoders=None, silence_typeerror=False, **json_kwargs):
		"""
		:param obj_encoders: An iterable of functions or encoder instances to try.
		:param silence_typeerror: If set to True, ignore the TypeErrors that Encoder instances throw (default False).
		"""
		self.obj_encoders = []
		if obj_encoders:
			self.obj_encoders = list(obj_encoders)
		self.silence_typeerror = silence_typeerror
		super(TricksEncoder, self).__init__(**json_kwargs)

	def default(self, obj, *args, **kwargs):
		"""
		This is the method of JSONEncoders that is called for each object; it calls
		all the encoders with the previous one's output used as input.

		It works for Encoder instances, but they are expected not to throw
		TypeErrorfor unrecognized types (the super method does that by default).

		It never calls the `super` method so if there are non-primitive types
		left at the end, you'll get an encoding error.
		"""
		prev_id = id(obj)
		for encoder in self.obj_encoders:
			if hasattr(encoder, 'default'):
				# hope no TypeError is thrown
				try:
					obj = encoder.default(obj)
				except TypeError as err:
					if not self.silence_typeerror:
						raise
			elif hasattr(encoder, '__call__'):
				obj = encoder(obj)
			else:
				raise TypeError('`obj_encoder` {0:} does not have `default` method and is not callable'.format(encoder))
		if id(obj) == prev_id:
			raise TypeError('Object of type {0:} could not be encoded by {1:} using encoders [{2:s}]'.format(
				type(obj), self.__class__.__name__, ', '.join(str(encoder) for encoder in self.obj_encoders)))
		return obj


def json_date_time_encode(obj):
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


def class_instance_encode(obj):
	"""
	Encodes a class instance to json. Note that it can only be recovered if the environment allows the class to be
	imported in the same way.
	"""
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
	return obj


class ClassInstanceEncoder(JSONEncoder):
	"""
	See `class_instance_encoder`.
	"""
	def __init__(self, obj, encode_cls_instances=True, **kwargs):
		self.encode_cls_instances = encode_cls_instances
		super(ClassInstanceEncoder, self).__init__(obj, **kwargs)

	def default(self, obj, *args, **kwargs):
		if self.encode_cls_instances:
			obj = class_instance_encode(obj)
		return super(ClassInstanceEncoder, self).default(obj, *args, **kwargs)


