
from copy import deepcopy
from json_tricks.np_utils import encode_scalars_inplace
from json_tricks.np import dumps, loads
from numpy import int8, int64, uint32, uint64, float16, float64, complex64, exp
from json_tricks.utils import hashodict


def test_dump_np_scalars():
	data = [
		int8(-27),
		complex64(exp(1)+37j),
		(
			{
				'alpha': float64(-exp(10)),
				'str-only': complex64(-1-1j),
			},
			uint32(123456789),
			float16(exp(-1)),
			{
				int64(37),
				uint64(-0),
			},
		),
	]
	replaced = encode_scalars_inplace(deepcopy(data))
	json = dumps(replaced)
	rec = loads(json)
	print(data)
	print(rec)
	assert data[0] == rec[0]
	assert data[1] == rec[1]
	assert data[2][0] == rec[2][0]
	assert data[2][1] == rec[2][1]
	assert data[2][2] == rec[2][2]
	assert data[2][3] == rec[2][3]
	assert data[2] == tuple(rec[2])

	
def test_hashodict():
	data = hashodict((('alpha', 37), ('beta', 42), ('gamma', -99)))
	assert tuple(data.keys()) == ('alpha', 'beta', 'gamma',)
	assert isinstance(hash(data), int)


