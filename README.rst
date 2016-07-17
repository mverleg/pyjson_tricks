JSON tricks (python)
---------------------------------------

Since the backward-incompatible 2.0 series, the `pyjson-tricks` package brings four pieces of functionality to python handling of json files:

1. **Store and load numpy arrays** in human-readable format.
2. **Store and load class instances** both generic and customized.
3. **Store and load date/times** as a dictionary (including timezone).
4. **Preserve map order** `{}` using `OrderedDict`.
5. **Allow for comments** in json files by starting lines with `#`.

As well as compression and disallowing duplicate keys.

* Code: https://github.com/mverleg/pyjson_tricks
* Documentation: http://json-tricks.readthedocs.org/en/latest/
* PIP: https://pypi.python.org/pypi/json_tricks

Several keys of the format `__keyname__` have special meanings, and more might be added in future releases.

Installation and use
---------------------------------------

You can install using

.. code-block:: bash

	pip install json-tricks

If your code relies on the old version, make sure to install

.. code-block:: bash

	pip install `json-tricks<2.0`

If you want to use numpy features, you should install numpy as well. If you don't, then numpy is not required.

You can import the usual json functions dump(s) and load(s), as well as a separate comment removal function, as follows:

.. code-block:: bash

	from json_tricks.np import dump, dumps, load, loads, strip_comments

If you do not have numpy and want to use only order preservation and commented json reading, you should **``import from json_tricks.nonp`` instead**.

The exact signatures of these functions are in the documentation_.

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

Class instances
+++++++++++++++++++++++++++++++++++++++

``json_tricks`` can serialize class instances.

If the class behaves normally (not generated dynamic, no ``__new__`` or ``__metaclass__`` magic, etc) *and* all it's attributes are serializable, then this should work by default.

.. code-block:: python

	# json_tricks/test_class.py
	class MyTestCls:
		def __init__(self, **kwargs):
			for k, v in kwargs.items():
				setattr(self, k, v)

	cls_instance = MyTestCls(s='ub', dct={'7': 7})

	json = dumps(cls_instance, indent=4)
	cls_instance_again = loads(json)

You'll get your instance back. Here the json looks like this:

.. code-block:: javascript

	{
		"__instance_type__": [
			"json_tricks.test_class",
			"MyTestCls"
		],
		"attributes": {
			"s": "ub",
			"dct": {
				"7": 7
			}
		}
	}

As you can see, this stores the module and class name. The class must be importable from the same module when decoding (and should not have changed).
If it isn't, you have to manually provide a dictionary to ``cls_lookup_map`` when loading in which the class name can be looked up. Note that if the class is imported, then ``globals()`` is such a dictionary (so try ``loads(json, cls_lookup_map=glboals())``).
Also note that if the class is defined in the 'top' script (that you're calling directly), then this isn't a module and the import part cannot be extracted. Only the class name will be stored; it can then only be deserialized in the same script, or if you provide ``cls_lookup_map``.

If the instance doesn't serialize automatically, or if you want custom behaviour, then you can implement ``__json__encode__(self)`` and ``__json_decode__(self, **attributes)`` methods, like so:

.. code-block:: python

	class CustomEncodeCls:
		def __init__(self):
			self.relevant = 42
			self.irrelevant = 37

		def __json_encode__(self):
			# should return primitive, serializable types like dict, list, int, string, float...
			return {'relevant': self.relevant}

		def __json_decode__(self, **attrs):
			# should initialize all properties; note that __init__ is not called implicitly
			self.relevant = attrs['relevant']
			self.irrelevant = 12

As you've seen, this uses the magic key `__instance_type__`. Don't use `__instance_type__` as a dictionary key unless you know what you're doing.

Date, time, datetime and timedelta
+++++++++++++++++++++++++++++++++++++++

Date, time, datetime and timedelta objects are stored as dictionaries of "day", "hour", "millisecond" etc keys, for each nonzero property. Timezone name is also stored in case it is set.

.. code-block:: javascript

	{
		"__datetime__": null,
		"year": 1988,
		"month": 3,
		"day": 15,
		"hour": 8,
		"minute": 3,
		"second": 59,
		"microsecond": 7,
		"tzinfo": "Europe/Amsterdam"
	}

This approach was chosen over timestamps for readability and consistency between date and time, and over a single string to prevent parsing problems and reduce dependencies.

To use timezones, `pytz` should be installed. If you try to decode a timezone-aware time or datetime without pytz, you will get an error.

Don't use `__date__`, `__time__`, `__datetime__`, `__timedelta__` or `__tzinfo__` as dictionary keys unless you know what you're doing, as they have special meaning.

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
	json = dumps(ordered)
	ordered = loads(json, preserve_order=True)

where `preserve_order=True` is added for emphasis; it can be left out since it's the default.

As a note on performance_, both dicts and OrderedDicts have the same scaling for getting and setting items (`O(1)`). In Python versions before 3.5, OrderedDicts were implemented in Python rather than C, so were somewhat slower; since Python 3.5 both are implemented in C. In summary, you should have no scaling problems and probably no performance problems at all, especially for 3.5 and later.

Comments
+++++++++++++++++++++++++++++++++++++++

This package uses ``#`` and ``//`` for comments, which seems to be the most common convention. For example, you could call `loads` on the following string::

	{ # "comment 1
		"hello": "Wor#d", "Bye": "\"M#rk\"", "yes\\\"": 5,# comment" 2
		"quote": "\"th#t's\" what she said", // comment "3"
		"list": [1, 1, "#", "\"", "\\", 8], "dict": {"q": 7} #" comment 4 with quotes
	}
	// comment 5

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

Other features
+++++++++++++++++++++++++++++++++++++++

* ``json_tricks`` allows for gzip compression using the ``compression=True`` argument (off by default).
* ``json_tricks`` can check for duplicate keys in maps by setting ``allow_duplicates`` to False. These are `kind of allowed`_, but are handled inconsistently between json implementations. In Python, for ``dict`` and ``OrderedDict``, duplicate keys are silently overwritten.

Usage & contributions
---------------------------------------

Revised BSD License; at your own risk, you can mostly do whatever you want with this code, just don't use my name for promotion and do keep the license file.

Contributions are welcome! Please test that the ``py.test`` tests still pass when sending a pull request.

.. _documentation: http://json-tricks.readthedocs.org/en/latest/#main-components
.. _stackoverflow: http://stackoverflow.com/questions/3488934/simplejson-and-numpy-array
.. _package: https://pypi.python.org/pypi/commentjson/
.. _pull: https://github.com/vaidik/commentjson/pull/11
.. _performance: http://stackoverflow.com/a/8177061/723090
.. _`kind of allowed`: http://stackoverflow.com/questions/21832701/does-json-syntax-allow-duplicate-keys-in-an-object


