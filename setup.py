from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    readme = fh.read()

def get_version_and_cmdclass(pkg_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.get_cmdclass(pkg_path)


version, cmdclass = get_version_and_cmdclass("ro_json")

setup(
    name='ro-json',
    version=version,
    cmdclass=cmdclass,
    description='Extra features for Python\'s JSON: comments, order, numpy, '
                'pandas, datetimes, and many more! Simple but customizable.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/ramonaoptics/ro-json',
    author='Clay Dugo',
    author_email='clay@ramonaoptics.com',
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=[
        'json',
        'numpy',
        'OrderedDict',
        'comments',
        'pandas',
        'pytz',
        'enum',
        'encode',
        'decode',
        'serialize',
        'deserialize',
        'roundtrip',
    ],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.10',
    project_urls={
        # 'Documentation': 'https://your-package-docs-url',
        'Source': 'https://github.com/ramonaoptics/ro_json',
        'Tracker': 'https://github.com/ramonaoptics/ro_json/issues',
    },
    license_files=('LICENSE.txt',),
)
