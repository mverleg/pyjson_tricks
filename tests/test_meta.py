
import re


def test_version():
	import json_tricks
	assert re.match(r'^\d+\.\d+\.\d+$', json_tricks.__version__) is not None
