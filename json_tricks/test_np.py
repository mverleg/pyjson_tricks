
from tempfile import mkdtemp
from copy import deepcopy
from numpy import arange, ones, array, array_equal, finfo, iinfo, exp
from os.path import join
from json_tricks.np_utils import encode_scalars_inplace
from .np import dump, dumps, load, loads
from .test_class import MyTestCls
from .test_nonp import cls_instance
from numpy import int8, int16, int32, int64, uint8, uint16, uint32, uint64, \
	float16, float32, float64, complex64, complex128


DTYPES = (int8, int16, int32, int64, uint8, uint16, uint32, uint64,
	float16, float32, float64, complex64, complex128)


def get_lims(dtype):
	try:
		info = finfo(dtype)
	except ValueError:
		info = iinfo(dtype)
	return dtype(info.min), dtype(info.max)


npdata = {
	'vector': arange(15, 70, 3, dtype=uint8),
	'matrix': ones((15, 10), dtype=float64),
}


def _numpy_equality(d2):
	assert npdata.keys() == d2.keys()
	assert (npdata['vector'] == d2['vector']).all()
	assert (npdata['matrix'] == d2['matrix']).all()
	assert npdata['vector'].dtype == d2['vector'].dtype
	assert npdata['matrix'].dtype == d2['matrix'].dtype


def test_dumps_loads_numpy():
	json = dumps(npdata)
	data2 = loads(json)
	_numpy_equality(data2)


def test_file_numpy():
	path = join(mkdtemp(), 'pytest-np.json')
	with open(path, 'wb+') as fh:
		dump(npdata, fh, compression=9)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	_numpy_equality(data2)


mixed_data = {
	'vec': array(range(10)),
	'inst': MyTestCls(
		nr=7, txt='yolo',
		li=[1,1,2,3,5,8,12],
		vec=array(range(7,16,2)),
		inst=cls_instance
	),
}


def test_mixed_cls_arr():
	json = dumps(mixed_data)
	back = dict(loads(json))
	assert mixed_data.keys() == back.keys()
	assert (mixed_data['vec'] == back['vec']).all()
	assert (mixed_data['inst'].vec == back['inst'].vec).all()
	assert (mixed_data['inst'].nr == back['inst'].nr)
	assert (mixed_data['inst'].li == back['inst'].li)
	assert (mixed_data['inst'].inst.s == back['inst'].inst.s)
	assert (mixed_data['inst'].inst.dct == dict(back['inst'].inst.dct))


def test_memory_order():
	arrC = array([[1., 2.], [3., 4.]], order='C')
	json = dumps(arrC)
	arr = loads(json)
	assert array_equal(arrC, arr)
	assert arrC.flags['C_CONTIGUOUS'] == arr.flags['C_CONTIGUOUS'] and \
		arrC.flags['F_CONTIGUOUS'] == arr.flags['F_CONTIGUOUS']
	arrF = array([[1., 2.], [3., 4.]], order='F')
	json = dumps(arrF)
	arr = loads(json)
	assert array_equal(arrF, arr)
	assert arrF.flags['C_CONTIGUOUS'] == arr.flags['C_CONTIGUOUS'] and \
		arrF.flags['F_CONTIGUOUS'] == arr.flags['F_CONTIGUOUS']


def test_scalars_types():
	# from: https://docs.scipy.org/doc/numpy/user/basics.types.html
	encme = []
	for dtype in DTYPES:
		for val in (dtype(0),) + get_lims(dtype):
			assert isinstance(val, dtype)
			encme.append(val)
	json = dumps(encme, indent=2)
	rec = loads(json)
	assert encme == rec


def test_array_types():
	# from: https://docs.scipy.org/doc/numpy/user/basics.types.html
	# see also `test_scalars_types`
	for dtype in DTYPES:
		vec = [array((dtype(0), dtype(exp(1))) + get_lims(dtype), dtype=dtype)]
		json = dumps(vec)
		assert dtype.__name__ in json
		rec = loads(json)
		assert rec[0].dtype == dtype
		assert array_equal(vec, rec)


def test_encode_scalar():
	encd = encode_scalars_inplace([complex128(1+2j)])
	print(encd)
	assert isinstance(encd[0], dict)
	assert encd[0]['__ndarray__'] == 1+2j
	assert encd[0]['shape'] == ()
	assert encd[0]['dtype'] == complex128.__name__


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


