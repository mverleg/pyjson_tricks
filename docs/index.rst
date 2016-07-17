
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

strip_comments
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.nonp.strip_comments

NumpyEncoder
+++++++++++++++++++++++++++++++++++++++

.. autoclass:: json_tricks.np.NumpyEncoder

json_numpy_obj_hook
+++++++++++++++++++++++++++++++++++++++

.. autofunction:: json_tricks.np.json_numpy_obj_hook

TricksPairHook
+++++++++++++++++++++++++++++++++++++++

.. autoclass:: json_tricks.nonp.TricksPairHook


Table of content
---------------------------------------

This is a simple module so the documentation is single-page.

.. toctree::
   :maxdepth: 2


