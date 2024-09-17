
.. include:: ../README.rst

Main components
---------------------------------------

Support for numpy, pandas and other libraries should work automatically if those libraries are installed. They are not installed automatically as dependencies because `json-tricks` can be used without them.

dumps
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.nonp.dumps

.. autofunction:: ro_json.np.dumps

dump
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.nonp.dump

.. autofunction:: ro_json.np.dump

loads
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.nonp.loads

.. autofunction:: ro_json.np.loads

load
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.nonp.load

.. autofunction:: ro_json.np.load

Utilities
---------------------------------------

strip comments
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.comment.strip_comments

numpy
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.np.numpy_encode

.. autofunction:: ro_json.np.json_numpy_obj_hook

class instances
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.encoders.class_instance_encode

.. autoclass:: json_tricks.decoders.ClassInstanceHook

enum instances
+++++++++++++++++++++++++++++++++++++++

Support for enums was added in Python 3.4. Support for previous versions of Python is available with the `enum 34`_ package.

.. autofunction:: ro_json.encoders.enum_instance_encode

.. autoclass:: json_tricks.decoders.EnumInstanceHook

By default ``IntEnum`` cannot be encoded as enums since they cannot be differenciated from integers. To serialize them, you must use `encode_intenums_inplace` which mutates a nested data structure (in place!) to replace any ``IntEnum`` by their representation. If you serialize this result, it can subsequently be loaded without further adaptations.

.. autofunction:: ro_json.utils.encode_intenums_inplace

date/time
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: ro_json.encoders.json_date_time_encode

.. autofunction:: ro_json.decoders.json_date_time_hook

numpy scalars
+++++++++++++++++++++++++++++++++++++++

It's not possible (without a lot of hacks) to encode numpy scalars. This is the case because some numpy scalars (`float64`, and depending on Python version also `int64`) are subclasses of `float` and `int`. This means that the Python json encoder will stringify them without them ever reaching the custom encoders.

So if you really want to encode numpy scalars, you'll have to do the conversion beforehand. For that purpose you can use `encode_scalars_inplace`, which mutates a nested data structure (in place!) to replace any numpy scalars by their representation. If you serialize this result, it can subsequently be loaded without further adaptations.

It's not great, but unless the Python json module changes, it's the best that can be done. See `issue 18`_ for more details.

.. autofunction:: ro_json.np_utils.encode_scalars_inplace

Table of content
---------------------------------------

This is a simple module so the documentation is single-page.

.. toctree::
   :maxdepth: 2


.. _`issue 18`: https://github.com/mverleg/pyjson_tricks/issues/18
.. _`enum 34`: https://pypi.org/project/enum34/


