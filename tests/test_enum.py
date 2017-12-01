#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from enum import Enum, IntEnum
from json_tricks import dumps, loads, encode_intenums_inplace


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
	json = '{"__enum__": {"__enum_instance_type__": [null, "MyEnum"], "attributes": {"name": "member1"}}}'
	back = loads(json, cls_lookup_map=globals())
	assert isinstance(back, MyEnum)
	assert back == MyEnum.member1


def test_enum_primitives():
	member = MyEnum.member1
	txt = dumps(member, primitives=True)
	assert txt == '"VALUE1"'


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
