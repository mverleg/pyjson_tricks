
How to run tests locally
===============================

If you want to, you can run the automated tests before using the code.

Note
-------------------------------

The tests run automatically on the supported versions of Python for every commit. You can check the TravisCI result at the bottom of the README on Github.

This file is only for if you want to run the tests on the exact code that you're getting through pip, using your local environment.

Setup
-------------------------------

First download the files using pip for the version you want to use (replace ``X.Y.Z`` by the version):

    pip download 'json_tricks==X.Y.Z'

There will be a compressed directory ``json_tricks-X.Y.Z.tar.gz``. Uncompress it and navigate to it's root. You should see ``json_tricks``, ``tests`` and a number of other things.

You will need to install ``pytest``, e.g. using ``pip install pytest``.

To test the full functionality, you will need to install

* ``pytz``
* ``numpy`` (note: doesn't work with pypy)
* ``pandas`` (note: doesn't work with pypy and does not supported python 3.4)
* ``enum34`` if you're on python 2.7 or pypy
* ``ordereddict`` on python 2.6 (which is not supported but might work)

If you want coverage information, also install ``pytest-coverage``.

Run
-------------------------------

To run all the tests (requiring you to have all the packages mentioned):

    py.test --continue-on-collection-errors

Using this flag, you will get a failure message when e.g. ``pandas`` is missing, but the other tests will still run.

You might see something like this on Python 3.5 with pytz and numpy but *without* pandas:

    collected 49 items / 1 errors

    json_tricks-3.11.1.1/tests/test_bare.py ....................... [ 46%]
    ......                                                          [ 59%]
    json_tricks-3.11.1.1/tests/test_enum.py .......                 [ 73%]
    json_tricks-3.11.1.1/tests/test_np.py .........                 [ 91%]
    json_tricks-3.11.1.1/tests/test_tz.py ..                        [ 95%]
    json_tricks-3.11.1.1/tests/test_utils.py ..                     [100%]

    =============================== ERRORS ================================
    _____ ERROR collecting json_tricks-3.11.1.1/tests/test_pandas.py ______
    ImportError while importing test module '/home/mark/TMP_jsontricks/json_tricks-3.11.1.1/tests/test_pandas.py'.
    Hint: make sure your test modules/packages have valid Python names.
    Traceback:
    json_tricks-3.11.1.1/tests/test_pandas.py:7: in <module>
        from pandas import DataFrame, Series
    E   ImportError: No module named 'pandas'
    ================= 49 passed, 1 error in 0.39 seconds ==================

which means that it worked! (Since the only error is the pandas one).

If you want to see test coverage, make sure you have ``pytest-coverage`` and run:

    py.test --cov json_tricks --cov-report=html --continue-on-collection-errors

You can then see your report in ``htmlcov/index.html`` (in a browser). Note that coverage is naturally lower if some tests are skipped due to missing packages.


