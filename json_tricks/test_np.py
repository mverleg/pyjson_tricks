
from tempfile import mkdtemp
from numpy import arange, ones, uint8, float64
from os.path import join
from .np import dump, dumps, load, loads


npdata = {
	'vector': arange(15, 70, 3, dtype=uint8),
	'matrix': ones((15, 10), dtype=float64),
}


def test_dumps_loads_numpy():
	json = dumps(npdata)
	data2 = loads(json)
	assert npdata.keys() == data2.keys()
	assert (npdata['vector'] == data2['vector']).all()
	assert (npdata['matrix'] == data2['matrix']).all()
	assert npdata['vector'].dtype == data2['vector'].dtype
	assert npdata['matrix'].dtype == data2['matrix'].dtype


def test_dump_load_numpy():
	path = join(mkdtemp(), 'pytest.json')
	with open(path, 'wb+') as fh:
		dump(npdata, fh, compression=9)
	with open(path, 'rb') as fh:
		data2 = load(fh, decompression=True)
	assert npdata.keys() == data2.keys()
	assert (npdata['vector'] == data2['vector']).all()
	assert (npdata['matrix'] == data2['matrix']).all()
	assert npdata['vector'].dtype == data2['vector'].dtype
	assert npdata['matrix'].dtype == data2['matrix'].dtype


