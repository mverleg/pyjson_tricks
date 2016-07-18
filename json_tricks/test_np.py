
from tempfile import mkdtemp
from numpy import arange, ones, uint8, float64, array
from os.path import join
from .np import dump, dumps, load, loads
from .test_class import MyTestCls
from .test_nonp import cls_instance


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


def test_dump_load_numpy():
	path = join(mkdtemp(), 'pytest.json')
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


