
import re


def test_version():
	import ro_json
	assert re.match(r'^\d+\.\d+\.\d+$', ro_json.__version__) is not None
