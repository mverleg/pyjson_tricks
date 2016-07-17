
from .comment import strip_comment_line_with_symbol, strip_comments
from .encoders import TricksEncoder, json_date_time_encode, class_instance_encode, ClassInstanceEncoder
from .decoders import DuplicateJsonKeyException, TricksPairHook, json_date_time_hook, ClassInstanceHook

try:
	# find_module takes just as long as importing, so no optimization possible
	import numpy
except ImportError:
	NUMPY_MODE = False
	from .nonp import dumps, dump, loads, load, NoNumpyException, json_nonumpy_obj_hook, json_nonumpy_obj_hook
else:
	NUMPY_MODE = True
	from .np import dumps, dump, loads, load, numpy_encode, NumpyEncoder, json_numpy_obj_hook


