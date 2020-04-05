
.. include:: ../README.rst

Main components
---------------------------------------

Support for numpy, pandas and other libraries should work automatically if those libraries are installed. They are not installed automatically as dependencies because `json-tricks` can be used without them.

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

enum instances
+++++++++++++++++++++++++++++++++++++++

Support for enums was added in Python 3.4. Support for previous versions of Python is available with the `enum 34`_ package.

.. autofunction:: json_tricks.encoders.enum_instance_encode

.. autoclass:: json_tricks.decoders.EnumInstanceHook

By default ``IntEnum`` cannot be encoded as enums since they cannot be differenciated from integers. To serialize them, you must use `encode_intenums_inplace` which mutates a nested data structure (in place!) to replace any ``IntEnum`` by their representation. If you serialize this result, it can subsequently be loaded without further adaptations.

.. autofunction:: json_tricks.utils.encode_intenums_inplace

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

Running tests
---------------------------------------

There are many test environments: with and without pandas, numpy or timezone support, and for each of the supported Python versions. You will need all the Python versions installed, as well as a number of packages available through pip. You can just install ``detox`` (``pip install detox``), and others will be installed automatically as dependencies or during tests (like ``numpy``, ``pandas``, ``pytz``, ``pytest``, ``pytest-cov`` and ``tox``).

To run all of these tests at once, simply run ``detox`` from the main directory. It usually takes roughly half a minute, but the first time takes longer because packages need to be installed.

To get coverage information from all these configurations, you first need to combine them using ``coverage combine .tox/coverage/*`` (once after each ``detox``). You can then show results normally, e.g. ``coverage report``. It should be about 90%.

If you want to show results in IntelliJ PyCharm with lines highlighted etc, you need several steps. First generate an XML-report with ``coverage xml``. Then the paths must be made to start at the root of the project, or be absolute, which can be done using ``sed 's/filename="\([^"]*\)"/filename="pyjson_tricks\/\1"/g' coverage.xml`` or manually using find and replace. Finally, you can load the report using ``Tools > Show code coverage data`` and use the green ``+``.

Table of content
---------------------------------------

This is a simple module so the documentation is single-page.

.. toctree::
   :maxdepth: 2


.. _`issue 18`: https://github.com/mverleg/pyjson_tricks/issues/18
.. _`enum 34`: https://pypi.org/project/enum34/


