# -*- coding: utf-8 -*-

from sys import version_info
from setuptools import setup


with open('README.rst', 'r') as fh:
	readme = fh.read()


requires = []
if version_info < (2, 7, 0):
	requires.append('ordereddict')


setup(
	name='json_tricks',
	description='Add features to json: en/decoding of numpy arrays, ' +
		'preservation of ordering and ignoring of comments in input',
	long_description=readme,
	url='https://github.com/mverleg/pyjson_tricks',
	author='Mark V',
	maintainer='(the author)',
	author_email='mdilligaf@gmail.com',
	license='Revised BSD License (LICENSE.txt)',
	keywords=['json', 'numpy', 'OrderedDict', 'comments',],
	version='3.8.0',
	packages=['json_tricks'],
	include_package_data=True,
	zip_safe=False,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Development Status :: 6 - Mature',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.6',  # it should work, but there's a problem with tests
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Software Development :: Libraries :: Python Modules',
		# 'Topic :: Documentation',
		# 'Topic :: Documentation :: Sphinx',
		# 'Topic :: Utilities',
	],
	install_requires=requires,
		# pytz for timezones (and tests)
		# pytest for tests
		# tox for tests
		# sphinx for documentation
		# numpy for numpy functionality
)


