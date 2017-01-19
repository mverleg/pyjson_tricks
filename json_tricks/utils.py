
from collections import OrderedDict


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
			argspec = getargspec(callable)
			return set(argspec.args)
	else:
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
	

