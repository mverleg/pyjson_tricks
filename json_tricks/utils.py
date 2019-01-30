
from collections import OrderedDict
from functools import partial
from importlib import import_module
from logging import warning, warn
from sys import version_info, version


class hashodict(OrderedDict):
	"""
	This dictionary is hashable. It should NOT be mutated, or all kinds of weird
	bugs may appear. This is not enforced though, it's only used for encoding.
	"""
	def __hash__(self):
		return hash(frozenset(self.items()))


try:
	from inspect import signature
except ImportError:
	try:
		from inspect import getfullargspec
	except ImportError:
		from inspect import getargspec
		def get_arg_names(callable):
			if type(callable) == partial and version_info[0] == 2:
				if not hasattr(get_arg_names, '__warned_partial_argspec'):
					get_arg_names.__warned_partial_argspec = True
					warn("'functools.partial' and 'inspect.getargspec' are not compatible in this Python version; "
						"ignoring the 'partial' wrapper when inspecting arguments of {}, which can lead to problems".format(callable))
				return set(getargspec(callable.func).args)
			argspec = getargspec(callable)
			return set(argspec.args)
	else:
		#todo: this is not covered in test case (py 3+ uses `signature`, py2 `getfullargspec`); consider removing it
		def get_arg_names(callable):
			argspec = getfullargspec(callable)
			return set(argspec.args) | set(argspec.kwonlyargs)
else:
	def get_arg_names(callable):
		sig = signature(callable)
		return set(sig.parameters.keys())


def call_with_optional_kwargs(callable, *args, **optional_kwargs):
	accepted_kwargs = get_arg_names(callable)
	use_kwargs = {}
	for key, val in optional_kwargs.items():
		if key in accepted_kwargs:
			use_kwargs[key] = val
	return callable(*args, **use_kwargs)


class NoNumpyException(Exception):
	""" Trying to use numpy features, but numpy cannot be found. """


class NoPandasException(Exception):
	""" Trying to use pandas features, but pandas cannot be found. """


class NoEnumException(Exception):
	""" Trying to use enum features, but enum cannot be found. """


class ClassInstanceHookBase(object):
	def __init__(self, cls_lookup_map=None):
		self.cls_lookup_map = cls_lookup_map or {}

	def get_cls_from_instance_type(self, mod, name):
		if mod is None:
			try:
				Cls = getattr((__import__('__main__')), name)
			except (ImportError, AttributeError) as err:
				if name not in self.cls_lookup_map:
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

		return Cls


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
	from numpy import generic, complex64, complex128
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


def encode_intenums_inplace(obj):
	"""
	Searches a data structure of lists, tuples and dicts for IntEnum
	and replaces them by their dictionary representation, which can be loaded
	by json-tricks. This happens in-place (the object is changed, use a copy).
	"""
	from enum import IntEnum
	from json_tricks import encoders
	if isinstance(obj, IntEnum):
		return encoders.enum_instance_encode(obj)
	if isinstance(obj, dict):
		for key, val in obj.items():
			obj[key] = encode_intenums_inplace(val)
		return obj
	if isinstance(obj, list):
		for index, val in enumerate(obj):
			obj[index] = encode_intenums_inplace(val)
		return obj
	if isinstance(obj, (tuple, set)):
		return type(obj)(encode_intenums_inplace(val) for val in obj)
	return obj


def get_module_name_from_object(obj):
	mod = obj.__class__.__module__
	if mod == '__main__':
		mod = None
		warning(('class {0:} seems to have been defined in the main file; unfortunately this means'
			' that it\'s module/import path is unknown, so you might have to provide cls_lookup_map when '
			'decoding').format(obj.__class__))
	return mod


def nested_index(collection, indices):
	for i in indices:
		collection = collection[i]
	return collection


is_py3 = (version[:2] == '3.')
str_type = str if is_py3 else (basestring, unicode,)

