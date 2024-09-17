#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from functools import partial
from enum import Enum, IntEnum
from ro_json import dumps, loads, encode_intenums_inplace
from ro_json.encoders import enum_instance_encode


PY2 = sys.version_info[0] == 2


class MyEnum(Enum):
	member1 = 'VALUE1'
	member2 = 'VALUE2'


class MyIntEnum(IntEnum):
	int_member = 1


def test_enum():
	member = MyEnum.member1
	txt = dumps(member)
	back = loads(txt)

	assert isinstance(back, MyEnum)
	assert back == member


def test_enum_instance_global():
	json = '{"__enum__": {"__enum_instance_type__": [null, "MyEnum"], "name": "member1"}}'
	back = loads(json, cls_lookup_map=globals())
	assert isinstance(back, MyEnum)
	assert back == MyEnum.member1


def test_enum_primitives():
	member = MyEnum.member1
	txt = dumps(member, primitives=True)
	assert txt == '{"member1": "VALUE1"}'


def test_encode_int_enum():
	member = MyIntEnum.int_member
	txt = dumps(member)
	# IntEnum are serialized as strings in enum34 for python < 3.4. This comes from how the JSON serializer work. We can't do anything about this besides documenting.
	# See https://bitbucket.org/stoneleaf/enum34/issues/17/difference-between-enum34-and-enum-json
	if PY2:
		assert txt == u"MyIntEnum.int_member"
	else:
		assert txt == "1"


def test_encode_int_enum_inplace():
	obj = {
		'int_member': MyIntEnum.int_member,
		'list': [MyIntEnum.int_member],
		'nested': {
			'member': MyIntEnum.int_member,
		}
	}

	txt = dumps(encode_intenums_inplace(obj))
	data = loads(txt)

	assert isinstance(data['int_member'], MyIntEnum)
	assert data['int_member'] == MyIntEnum.int_member
	assert isinstance(data['list'][0], MyIntEnum)
	assert isinstance(data['nested']['member'], MyIntEnum)


class EnumValueTest(object):
	alpha = 37
	def __init__(self, beta):
		self.beta = beta


class CombineComplexTypesEnum(Enum):
	class_inst = EnumValueTest(beta=42)
	timepoint = datetime(year=1988, month=3, day=15, hour=8, minute=3, second=59, microsecond=7)
	img = 1j


def test_complex_types_enum():
	obj = [
		CombineComplexTypesEnum.timepoint,
		CombineComplexTypesEnum.img,
		CombineComplexTypesEnum.class_inst,
	]
	txt = dumps(encode_intenums_inplace(obj))
	back = loads(txt)
	assert obj == back


def test_with_value():
	obj = [CombineComplexTypesEnum.class_inst, CombineComplexTypesEnum.timepoint]
	encoder = partial(enum_instance_encode, with_enum_value=True)
	txt = dumps(obj, extra_obj_encoders=(encoder,))
	assert '"value":' in txt
	back = loads(txt, obj_pairs_hooks=())
	class_inst_encoding = loads(dumps(CombineComplexTypesEnum.class_inst.value), obj_pairs_hooks=())
	timepoint_encoding = loads(dumps(CombineComplexTypesEnum.timepoint.value), obj_pairs_hooks=())
	assert back[0]['__enum__']['value'] == class_inst_encoding
	assert back[1]['__enum__']['value'] == timepoint_encoding


