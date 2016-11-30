
from collections import OrderedDict


class hashodict(OrderedDict):
	"""
	This dictionary is hashable. It should NOT be mutated, or all kinds of weird
	bugs may appear. This is not enforced though, it's only used for encoding.
	"""
	def __hash__(self):
		return hash(frozenset(self.items()))


