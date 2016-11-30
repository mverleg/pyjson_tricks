
from .comment import strip_comment_line_with_symbol, strip_comments
from .encoders import TricksEncoder, json_date_time_encode, class_instance_encode, ClassInstanceEncoder
from .decoders import DuplicateJsonKeyException, TricksPairHook, json_date_time_hook, ClassInstanceHook

try:
	# find_module takes just as long as importing, so no optimization possible
	import numpy
except ImportError:
	NUMPY_MODE = False
	from .nonp import dumps, dump, loads, load, nonumpy_encode as numpy_encode, json_nonumpy_obj_hook as json_numpy_obj_hook, NoNumpyException
else:
	NUMPY_MODE = True
	from .np import dumps, dump, loads, load, numpy_encode, NumpyEncoder, json_numpy_obj_hook, NoNumpyException
	from .np_utils import encode_scalars_inplace


