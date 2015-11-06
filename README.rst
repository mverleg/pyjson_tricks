JSON tricks (python)
---------------------------------------

At this time, the `pyjson-tricks` package brings three pieces of functionality to python handling of json files:

1. **Store and load numpy arrays** in human-readable format.
2. **Preserve map order** `{}` using `OrderedDict`.
3. **Allow for comments** in json files by starting lines with `#`.

It also allows for gzip compression using the `compress=True` argument (off by default).

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

This package uses `#` for comments, which seems to be the most common convention. For example, you could call `loads` on the following string:

.. code-block:: 

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

There is already a `commentjson` package_ for Python. However, as of November 2015, it doesn't support Python 3.x, and a pull_ request to add support has been left pending for five months.

The implementation of comments is not particularly efficient, but it does handle all the special cases I tested. For a few files you shouldn't notice any performance problems, but if you're reading hundreds of files, then they are presumably computer-generated, and you could consider turning comments off (`strip_comments=False`).

License
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.

.. _stackoverflow: http://stackoverflow.com/questions/3488934/simplejson-and-numpy-array
.. _package: https://pypi.python.org/pypi/commentjson/
.. _pull: https://github.com/vaidik/commentjson/pull/11
.. _performance: http://stackoverflow.com/a/8177061/723090

