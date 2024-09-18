> [!NOTE]
>The primary reason for this fork is to enable full round-trip serialization and deserialization of NumPy scalars and 0-dimensional arrays to JSON and back. This feature is essential for applications that require precise data preservation when working with NumPy data types.

Despite contributing this enhancement to the original project (see [Pull Request #99](https://github.com/mverleg/pyjson_tricks/pull/99)), there was a difference in opinion with the maintainer regarding its inclusion. As a result, this fork aims to continue development with this functionality integrated.

# ro_json

The [ro-json] package brings several pieces of
functionality to python handling of json files:

1.  **Store and load numpy arrays** in human-readable format.
2.  **Store and load class instances** both generic and customized.
3.  **Store and load date/times** as a dictionary (including timezone).
4.  **Preserve map order** `{}` using `OrderedDict`.
5.  **Allow for comments** in json files by starting lines with `#`.
6.  Sets, complex numbers, Decimal, Fraction, enums, compression,
    duplicate keys, pathlib Paths, bytes ...

As well as compression and disallowing duplicate keys.

* Code: <https://github.com/ramonaoptics/ro-json>
<!-- * Documentation: <http://ro-json.readthedocs.org/en/latest/> -->
* PIP: <https://pypi.python.org/pypi/ro-json>

Several keys of the format `__keyname__` have special meanings, and more
might be added in future releases.

If you're considering JSON-but-with-comments as a config file format,
have a look at [HJSON](https://github.com/hjson/hjson-py), it might be
more appropriate. For other purposes, keep reading!

Thanks for all the Github stars⭐!

# Installation and use

You can install using

``` bash
pip install ro_json
```

Decoding of some data types needs the corresponding package to be
installed, e.g. `numpy` for arrays, `pandas` for dataframes and `pytz`
for timezone-aware datetimes.

You can import the usual json functions dump(s) and load(s), as well as
a separate comment removal function, as follows:

``` bash
from ro_json import dump, dumps, load, loads, strip_comments
```

The exact signatures of these and other functions are in the [documentation](http://json-tricks.readthedocs.org/en/latest/#main-components).

Quite some older versions of Python are supported. For an up-to-date  list see [the automated tests](./.github/workflows/tests.yml).

# Features

## Numpy arrays

When not compressed, the array is encoded in sort-of-readable and very
flexible and portable format, like so:

``` python
arr = arange(0, 10, 1, dtype=uint8).reshape((2, 5))
print(dumps({'mydata': arr}))
```

this yields:

``` javascript
{
    "mydata": {
        "dtype": "uint8",
        "shape": [2, 5],
        "Corder": true,
        "__ndarray__": [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    }
}
```

which will be converted back to a numpy array when using
`ro_json.loads`. Note that the memory order (`Corder`) is only
stored in v3.1 and later and for arrays with at least 2 dimensions.

As you see, this uses the magic key `__ndarray__`. Don't use
`__ndarray__` as a dictionary key unless you're trying to make a numpy
array (and know what you're doing).

Numpy scalars are also serialized (v3.5+). They are represented by the
closest python primitive type. A special representation was not
feasible, because Python's json implementation serializes some numpy
types as primitives, without consulting custom encoders. If you want to
preserve the exact numpy type, use
[encode_scalars_inplace](https://json-tricks.readthedocs.io/en/latest/#ro_json.np_utils.encode_scalars_inplace).

There is also a compressed format (thanks `claydugo` for fix). From
the next major release, this will be default when using compression.
For now, you can use it as:

``` python
dumps(data, compression=True, properties={'ndarray_compact': True})
```

This compressed format encodes the array data in base64, with gzip
compression for the array, unless 1) compression has little effect for
that array, or 2) the whole file is already compressed. If you only want
compact format for large arrays, pass the number of elements to
`ndarray_compact`.

Example:

``` python
data = [linspace(0, 10, 9), array([pi, exp(1)])]
dumps(data, compression=False, properties={'ndarray_compact': 8})

[{
   "__ndarray__": "b64.gz:H4sIAAAAAAAC/2NgQAZf7CE0iwOE5oPSIlBaEkrLQegGRShfxQEAz7QFikgAAAA=",
   "dtype": "float64",
   "shape": [9]
 }, {
   "__ndarray__": [3.141592653589793, 2.718281828459045],
   "dtype": "float64",
   "shape": [2]
 }]
```

## Class instances

`ro_json` can serialize class instances.

If the class behaves normally (not generated dynamic, no `__new__` or
`__metaclass__` magic, etc) *and* all it's attributes are serializable,
then this should work by default.

``` python
# ro_json/test_class.py
class MyTestCls:
def __init__(self, **kwargs):
    for k, v in kwargs.items():
        setattr(self, k, v)

cls_instance = MyTestCls(s='ub', dct={'7': 7})

json = dumps(cls_instance, indent=4)
cls_instance_again = loads(json)
```

You'll get your instance back. Here the json looks like this:

``` javascript
{
   	"__instance_type__": [
   		"ro_json.test_class",
   		"MyTestCls"
   	],
   	"attributes": {
   		"s": "ub",
   		"dct": {
   			"7": 7
   		}
   	}
}
```

As you can see, this stores the module and class name. The class must be
importable from the same module when decoding (and should not have
changed). If it isn't, you have to manually provide a dictionary to
`cls_lookup_map` when loading in which the class name can be looked up.
Note that if the class is imported, then `globals()` is such a
dictionary (so try `loads(json, cls_lookup_map=glboals())`). Also note
that if the class is defined in the 'top' script (that you're calling
directly), then this isn't a module and the import part cannot be
extracted. Only the class name will be stored; it can then only be
deserialized in the same script, or if you provide `cls_lookup_map`.

Note that this also works with `slots` without having to do anything
(thanks to `koffie` and `dominicdoty`), which encodes like this (custom
indentation):

``` javascript
{
    "__instance_type__": ["module.path", "ClassName"],
    "slots": {"slotattr": 37},
    "attributes": {"dictattr": 42}
}
```

If the instance doesn't serialize automatically, or if you want custom
behaviour, then you can implement `__json__encode__(self)` and
`__json_decode__(self, **attributes)` methods, like so:

``` python
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
```

As you've seen, this uses the magic key `__instance_type__`. Don't use
`__instance_type__` as a dictionary key unless you know what you're
doing.

## Date, time, datetime and timedelta

Date, time, datetime and timedelta objects are stored as dictionaries of
"day", "hour", "millisecond" etc keys, for each nonzero property.

Timezone name is also stored in case it is set, as is DST (thanks `eumir`).
You'll need to have `pytz` installed to use timezone-aware date/times,
it's not needed for naive date/times.

``` javascript
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
```

This approach was chosen over timestamps for readability and consistency
between date and time, and over a single string to prevent parsing
problems and reduce dependencies. Note that if `primitives=True`,
date/times are encoded as ISO 8601, but they won't be restored
automatically.

Don't use `__date__`, `__time__`, `__datetime__`, `__timedelta__` or
`__tzinfo__` as dictionary keys unless you know what you're doing, as
they have special meaning.

## Order

Given an ordered dictionary like this (see the tests for a longer one):

``` python
ordered = OrderedDict((
    ('elephant', None),
    ('chicken', None),
    ('tortoise', None),
))
```

Converting to json and back will preserve the order:

``` python
from ro_json import dumps, loads
json = dumps(ordered)
ordered = loads(json, preserve_order=True)
```

where `preserve_order=True` is added for emphasis; it can be left out
since it's the default.

As a note on [performance](http://stackoverflow.com/a/8177061/723090),
both dicts and OrderedDicts have the same scaling for getting and
setting items (`O(1)`). In Python versions before 3.5, OrderedDicts were
implemented in Python rather than C, so were somewhat slower; since
Python 3.5 both are implemented in C. In summary, you should have no
scaling problems and probably no performance problems at all, especially
in Python 3. Python 3.6+ preserves order of dictionaries by default
making this redundant, but this is an implementation detail that should
not be relied on.

## Comments

*Warning: in the next major version, comment parsing will be opt-in, not
default anymore (for performance reasons). Update your code now to pass
`ignore_comments=True` explicitly if you want comment parsing.*

This package uses `#` and `//` for comments, which seem to be the most
common conventions, though only the latter is valid javascript.

For example, you could call `loads` on the following string:

{ # "comment 1
    "hello": "Wor#d", "Bye": ""M#rk"", "yes\\"": 5,# comment" 2
    "quote": ""th#t's" what she said", // comment "3"
    "list": [1, 1, "#", """, "\", 8], "dict": {"q": 7} #" comment 4 with quotes
}
// comment 5

And it would return the de-commented version:

``` javascript
{
    "hello": "Wor#d", "Bye": ""M#rk"", "yes\\"": 5,
    "quote": ""th#t's" what she said",
    "list": [1, 1, "#", """, "\", 8], "dict": {"q": 7}
}
```

Since comments aren't stored in the Python representation of the data,
loading and then saving a json file will remove the comments (it also
likely changes the indentation).

The implementation of comments is a bit crude, which means that there are
some exceptional cases that aren't handled correctly ([#57](https://github.com/mverleg/pyjson_tricks/issues/57)).

It is also not very fast. For that reason, if `ignore_comments` wasn't
explicitly set to True, then ro_json first tries to parse without
ignoring comments. If that fails, then it will automatically re-try
with comment handling. This makes the no-comment case faster at the cost
of the comment case, so if you are expecting comments make sure to set
`ignore_comments` to True.

## Other features

* Special floats like `NaN`, `Infinity` and
  `-0` using the `allow_nan=True` argument
  ([non-standard](https://stackoverflow.com/questions/1423081/json-left-out-infinity-and-nan-json-status-in-ecmascript)
  json, may not decode in other implementations).
* Sets are serializable and can be loaded. By default the set json
  representation is sorted, to have a consistent representation.
* Save and load complex numbers (py3) with `1+2j` serializing as
  `{'__complex__': [1, 2]}`.
* Save and load `Decimal` and `Fraction` (including NaN, infinity, -0
  for Decimal).
* Save and load `Enum` (thanks to `Jenselme`), either built-in in
  python3.4+, or with the [enum34](https://pypi.org/project/enum34/)
  package in earlier versions. `IntEnum` needs
  [encode_intenums_inplace](https://json-tricks.readthedocs.io/en/latest/#ro_json.utils.encode_intenums_inplace).
* `ro_json` allows for gzip compression using the
  `compression=True` argument (off by default).
* `ro_json` can check for duplicate keys in maps by setting
  `allow_duplicates` to False. These are [kind of
  allowed](http://stackoverflow.com/questions/21832701/does-json-syntax-allow-duplicate-keys-in-an-object),
  but are handled inconsistently between json implementations. In
  Python, for `dict` and `OrderedDict`, duplicate keys are silently
  overwritten.
* Save and load `pathlib.Path` objects (e.g., the current path,
  `Path('.')`, serializes as `{"__pathlib__": "."}`)
  (thanks to `bburan`).
* Save and load bytes (python 3+ only), which will be encoded as utf8 if
  that is valid, or as base64 otherwise. Base64 is always used if
  primitives are requested. Serialized as
  `[{"__bytes_b64__": "aGVsbG8="}]` vs `[{"__bytes_utf8__": "hello"}]`.
* Save and load slices (thanks to `claydugo`).

# Preserve type vs use primitive

By default, types are encoded such that they can be restored to their
original type when loaded with `ro-json`. Example encodings in this
documentation refer to that format.

You can also choose to store things as their closest primitive type
(e.g. arrays and sets as lists, decimals as floats). This may be
desirable if you don't care about the exact type, or you are loading
the json in another language (which doesn't restore python types).
It's also smaller.

To forego meta data and store primitives instead, pass `primitives` to
`dump(s)`. This is available in version `3.8` and later. Example:

``` python
data = [
    arange(0, 10, 1, dtype=int).reshape((2, 5)),
    datetime(year=2017, month=1, day=19, hour=23, minute=00, second=00),
    1 + 2j,
    Decimal(42),
    Fraction(1, 3),
    MyTestCls(s='ub', dct={'7': 7}),  # see later
    set(range(7)),
]
# Encode with metadata to preserve types when decoding
print(dumps(data))
```

``` javascript

// (comments added and indenting changed)
[
    // numpy array
    {
        "__ndarray__": [
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8, 9]],
        "dtype": "int64",
        "shape": [2, 5],
        "Corder": true
    },
    // datetime (naive)
    {
        "__datetime__": null,
        "year": 2017,
        "month": 1,
        "day": 19,
        "hour": 23
    },
    // complex number
    {
        "__complex__": [1.0, 2.0]
    },
    // decimal & fraction
    {
        "__decimal__": "42"
    },
    {
        "__fraction__": true
        "numerator": 1,
        "denominator": 3,
    },
    // class instance
    {
        "__instance_type__": [
          "tests.test_class",
          "MyTestCls"
        ],
        "attributes": {
          "s": "ub",
          "dct": {"7": 7}
        }
    },
    // set
    {
        "__set__": [0, 1, 2, 3, 4, 5, 6]
    }
]
```

``` python
# Encode as primitive types; more simple but loses type information
print(dumps(data, primitives=True))
```

``` javascript
// (comments added and indentation changed)
[
    // numpy array
    [[0, 1, 2, 3, 4],
    [5, 6, 7, 8, 9]],
    // datetime (naive)
    "2017-01-19T23:00:00",
    // complex number
    [1.0, 2.0],
    // decimal & fraction
    42.0,
    0.3333333333333333,
    // class instance
    {
        "s": "ub",
        "dct": {"7": 7}
    },
    // set
    [0, 1, 2, 3, 4, 5, 6]
]
```

Note that valid json is produced either way: ``ro_json`` stores meta data as normal json, but other packages probably won't interpret it.

Note that valid json is produced either way: `ro_json` stores meta
data as normal json, but other packages probably won't interpret it.

# Usage & contributions

Code is under [Revised BSD License](LICENSE.txt)
so you can use it for most purposes including commercially.

Contributions are very welcome! Bug reports, feature suggestions and
code contributions help this project become more useful for everyone!
There is a short [contribution
guide](CONTRIBUTING.md).

Contributors not yet mentioned: `janLo` (performance boost).

# Tests

Tests are run automatically for commits to the repository for all
supported versions. This is the status:

To run the tests manually for your version, see [this guide](tests/run_locally.md).
