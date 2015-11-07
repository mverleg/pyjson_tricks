JSON tricks (python)
---------------------------------------

At this time, the `pyjson-tricks` package brings three pieces of functionality to python handling of json files:

1. **Store and load numpy arrays** in human-readable format.
2. **Preserve map order** `{}` using `OrderedDict`.
3. **Allow for comments** in json files by starting lines with `#`.

It also allows for gzip compression using the ``compress=True`` argument (off by default).

* Code: https://github.com/mverleg/pyjson_tricks
* Documentation: http://json-tricks.readthedocs.org/en/latest/
* PIP: https://pypi.python.org/pypi/json_tricks

Installation and use
---------------------------------------

You can install using

.. code-block:: bash

	pip install json-tricks

If you want to use numpy features, you should install numpy as well. If you don't, then numpy is not required.

You can import the usual json functions dump(s) and load(s), as well as a separate comment removal function, as follows:

.. code-block:: bash

	from json_tricks.np import dump, dumps, load, loads, strip_comments

If you do not have numpy and want to use only order preservation and commented json reading, you should **import from json_tricks.nonp`` instead**.

The exact signatures of these functions are in the documentation_. In many cases, keeping the arguments of the standard json functions but changing the import will be enough to use the extra features.

Features
---------------------------------------

Numpy arrays
+++++++++++++++++++++++++++++++++++++++

This implementation is mostly based on an answer by tlausch on stackoverflow_ that you could read for details.

The array is encoded in sort-of-readableformat, like so:

.. code-block:: python

	arr = arange(0, 10, 1, dtype=uint8).reshape((2, 5))
	print dumps({'mydata': arr})

after indering this yields:

.. code-block:: javascript

	{
		"mydata": {
			"dtype": "uint8",
			"shape": [2, 5],
			"__ndarray__": [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
		}
	}

which will be converted back to a numpy array when using `json_tricks.loads`.

As you've seen, this uses the magic key `__ndarray__`. Don't use `__ndarray__` as a dictionary key unless you're trying to make a numpy array (and know what you're doing).

Order
+++++++++++++++++++++++++++++++++++++++

Given an ordered dictionary like this (see the tests for a longer one):

.. code-block:: python

	ordered = OrderedDict((
		('elephant', None),
		('chicken', None),
		('tortoise', None),
	))

Converting to json and back will preserve the order:

.. code-block:: python

	from json_tricks import dumps, loads
	json = dumps(ordered, preserve_order=True)
	ordered = loads(json, preserve_order=True)

where `preserve_order=True` is added for emphasis; it can be left out since it's the default.

As a note on performance_, both dicts and OrderedDicts have the same scaling for getting and setting items (`O(1)`). In Python versions before 3.5, OrderedDicts were implemented in Python rather than C, so were somewhat slower; since Python 3.5 both are implemented in C. In summary, you should have no scaling problems and probably no performance problems at all, especially for 3.5 and later.

Comments
+++++++++++++++++++++++++++++++++++++++

This package uses `#` for comments, which seems to be the most common convention. For example, you could call `loads` on the following string::

	{ # "comment 1
		"hello": "Wor#d", "Bye": "\"M#rk\"", "yes\\\"": 5,# comment" 2
		"quote": "\"th#t's\" what she said", # comment "3"
		"list": [1, 1, "#", "\"", "\\", 8], "dict": {"q": 7} #" comment 4 with quotes
	}
	# comment 5

And it would return the de-commented version:

.. code-block:: javascript

	{
		"hello": "Wor#d", "Bye": "\"M#rk\"", "yes\\\"": 5,
		"quote": "\"th#t's\" what she said",
		"list": [1, 1, "#", "\"", "\\", 8], "dict": {"q": 7}
	}

Since comments aren't stored in the Python representation of the data, loading and then saving a json file will remove the comments (it also likely changes the indentation).

There is already a `commentjson` package_ for Python. However, as of November 2015, it doesn't support Python 3.x, and a pull_ request to add support has been left pending for five months.

The implementation of comments is not particularly efficient, but it does handle all the special cases I tested. For a few files you shouldn't notice any performance problems, but if you're reading hundreds of files, then they are presumably computer-generated, and you could consider turning comments off (`ignore_comments=False`).

License
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.

.. _documentation: http://json-tricks.readthedocs.org/en/latest/#main-components
.. _stackoverflow: http://stackoverflow.com/questions/3488934/simplejson-and-numpy-array
.. _package: https://pypi.python.org/pypi/commentjson/
.. _pull: https://github.com/vaidik/commentjson/pull/11
.. _performance: http://stackoverflow.com/a/8177061/723090


