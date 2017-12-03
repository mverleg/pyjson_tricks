#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


