
How to run tests locally
===============================

If you want to, you can run the automated tests before using the code.

Note
-------------------------------

The tests run automatically on the supported versions of Python for every commit. You can check the Github Actions result at the bottom of the README on Github.

Run current verison
-------------------------------

To run py.test for current Python version, install requirements::

    pip install numpy pytz pandas pathlib ordereddict pytest-coverage

To run all the tests (requiring you to have all the packages mentioned)::

    py.test --continue-on-collection-errors

Using this flag, you will get a failure message when e.g. ``pandas`` is missing, but the other tests will still run.

Example output
-------------------------------

Output if all tests pass::

    platform linux -- Python 3.6.8, pytest-5.3.1, py-1.8.1, pluggy-0.13.1
    rootdir: /home/mark/pyjson_tricks
    plugins: cov-2.10.1
    collected 80 items

    tests/test_bare.py .......................................                                                       [ 48%]
    tests/test_enum.py .......                                                                                       [ 57%]
    tests/test_meta.py .                                                                                             [ 58%]
    tests/test_np.py .......................                                                                         [ 87%]
    tests/test_pandas.py ...                                                                                         [ 91%]
    tests/test_pathlib.py .                                                                                          [ 92%]
    tests/test_tz.py ...                                                                                             [ 96%]
    tests/test_utils.py ...                                                                                          [100%]

    80 passed, 4 warnings in 0.41s
