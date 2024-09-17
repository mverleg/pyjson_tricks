#!/usr/bin/env python
# -*- coding: utf-8 -*-

import weakref
from ro_json import dumps, loads


class MyTestCls(object):
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)

	def __repr__(self):
		return 'A<{0:}>'.format(', '.join('{0:s}={1:}'.format(k, v) for k, v in self.__dict__.items()))


class CustomEncodeCls(MyTestCls):
	def __init__(self, **kwargs):
		super(CustomEncodeCls, self).__init__(**kwargs)
		self.relevant = 42
		self.irrelevant = 37

	def __json_encode__(self):
		return {'relevant': self.relevant}

	def __json_decode__(self, **attrs):
		self.relevant = attrs['relevant']
		self.irrelevant = 12


class SuperClass(object):
	cls_attr = 37
	
	def __init__(self):
		self.attr = None
	
	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.__dict__ == other.__dict__


class SubClass(SuperClass):
	def set_attr(self):
		self.attr = 42


class SlotsBase(object):
	__slots__ = []
	
	def __eq__(self, other):
		if self.__class__ != other.__class__:
			return False
		slots = self.__class__.__slots__
		if isinstance(slots,str):
			slots = [slots]
		return all(getattr(self, i) == getattr(other, i) for i in slots)


class SlotsDictABC(SlotsBase):
	__slots__ = ['__dict__']
	
	def __init__(self, a='a', b='b', c='c'):
		self.a = a
		self.b = b
		self.c = c


class SlotsStr(SlotsBase):
	__slots__ = 'name'
	
	def __init__(self, name='name'):
		self.name = name


class SlotsABCDict(SlotsBase):
	__slots__ = ['a','b','c','__dict__']
	
	def __init__(self, a='a', b='b', c='c'):
		self.a = a
		self.b = b
		self.c = c


class SlotsABC(SlotsBase):
	__slots__ = ['a','b','c']
	
	def __init__(self, a='a', b='b', c='c'):
		self.a = a
		self.b = b
		self.c = c


def test_slots_weakref():
	""" Issue with attrs library due to __weakref__ in __slots__ https://github.com/mverleg/pyjson_tricks/issues/82 """
	class TestClass(object):
		__slots__ = "value", "__weakref__"
		def __init__(self, value):
			self.value = value

	obj = TestClass(value=7)
	json = dumps(obj)
	assert '__weakref__' not in json
	decoded = loads(json, cls_lookup_map=dict(TestClass=TestClass))
	assert obj.value == decoded.value


def test_pure_weakref():
	""" Check that the issue in `test_slots_weakref` does not happen without __slots__ """
	obj = MyTestCls(value=7)
	ref = weakref.ref(obj)
	json = dumps(obj)
	decoded = loads(json)
	assert str(obj) == str(decoded)
	# noinspection PyUnusedLocal
	obj = None
	assert ref() is None

