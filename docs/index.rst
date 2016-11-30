
.. include:: ../README.rst

Main components
---------------------------------------

Note that these functions exist as two versions, the full version with numpy (np) and the version without requirements (nonp) that doesn't do nunpy encoding/decoding.

If you import these functions directly from json_tricks, e.g. ``from json_tricks import dumps``, then it will select np if numpy is available, and nonp otherwise. You can use ``json_tricks.NUMPY_MODE`` to see if numpy mode is being used.

This dual behaviour can lead to confusion, so it is recommended that you import directly from np or nonp.

dumps
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.nonp.dumps

.. autofunction:: json_tricks.np.dumps

dump
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.nonp.dump

.. autofunction:: json_tricks.np.dump

loads
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.nonp.loads

.. autofunction:: json_tricks.np.loads

load
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.nonp.load

.. autofunction:: json_tricks.np.load

Utilities
---------------------------------------

strip comments
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.comment.strip_comments

numpy
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.np.numpy_encode

.. autofunction:: json_tricks.np.json_numpy_obj_hook

class instances
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.encoders.class_instance_encode

.. autoclass:: json_tricks.decoders.ClassInstanceHook

date/time
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.encoders.json_date_time_encode

.. autofunction:: json_tricks.decoders.json_date_time_hook

numpy scalars
+++++++++++++++++++++++++++++++++++++++

It's not possible (without a lot of hacks) to encode numpy scalars. This is the case because some numpy scalars (`float64`, and depending on Python version also `int64`) are subclasses of `float` and `int`. This means that the Python json encoder will stringify them without them ever reaching the custom encoders.

So if you really want to encode numpy scalars, you'll have to do the conversion beforehand. For that purpose you can use `encode_scalars_inplace`, which mutates a nested data structure (in place!) to replace any numpy scalars by their representation. If you serialize this result, it can subsequently be loaded without further adaptations.

It's not great, but unless the Python json module changes, it's the best that can be done. See `issue 18`_ for more details.

.. autofunction:: json_tricks.np_utils.encode_scalars_inplace


Table of content
---------------------------------------

This is a simple module so the documentation is single-page.

.. toctree::
   :maxdepth: 2


.. _`issue 18`: https://github.com/mverleg/pyjson_tricks/issues/18


