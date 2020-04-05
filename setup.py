# -*- coding: utf-8 -*-

from sys import version_info
import warnings

from setuptools import setup

with open('README.rst', 'r') as fh:
	readme = fh.read()

# with open('json_tricks/_version.py', 'r') as fh:
# 	version = fh.read().strip()
from json_tricks._version import VERSION

requires = []
if version_info < (2, 7, 0):
	requires.append('ordereddict')

if (version_info[0] == 2 and version_info[1] < 7) or \
		(version_info[0] == 3 and version_info[1] < 4) or \
		version_info[0] not in (2, 3):
	raise warnings.warn('`json_tricks` does not support Python version {}.{}'
		.format(version_info[0], version_info[1]))

setup(
	name='json_tricks',
	description='Extra features for Python\'s JSON: comments, order, numpy, '
		'pandas, datetimes, and many more! Simple but customizable.',
	long_description=readme,
	url='https://github.com/mverleg/pyjson_tricks',
	author='Mark V',
	maintainer='Mark V',
	author_email='markv.nl.dev@gmail.com',
	license='Revised BSD License (LICENSE.txt)',
	keywords=['json', 'numpy', 'OrderedDict', 'comments', 'pandas', 'pytz',
		'enum', 'encode', 'decode', 'serialize', 'deserialize'],
	version=VERSION,
	packages=['json_tricks'],
	package_data=dict(
		json_tricks=['LICENSE.txt', 'README.rst', 'VERSION'],
		# tests=['tests/*.py'],
	),
	# include_package_data=True,
	zip_safe=True,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Development Status :: 6 - Mature',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Topic :: Software Development :: Libraries :: Python Modules',
		# 'Topic :: Utilities',
	],
	install_requires=requires,
)
