# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Required packages for install, test, docs, and tests."""

import os
import re

from setuptools import setup, find_packages


install_requires = [
    'future',
    'pandas>=1.0.0',
    'pyyaml>=5.1',
    'jsonschema',
    'SQLAlchemy>=1.3.18',
    'requests',
    'Click>=7.0.0'
]


tests_require = [
    'coverage>=5.0',
    'pytest',
    'pytest-cov'
]


dev_require = [
    'flake8',
    'python-language-server',
    'mypy',
    'pylint',
    'pydocstyle'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme',
        'sphinxcontrib-apidoc',
        'jupyter-sphinx',
        'nbshpinx',
        'nbsphinx-link'
    ],
    'tests': tests_require,
    'dev': dev_require + tests_require
}


# Get the version string from the version.py file in the refdata package.
# Based on:
# https://stackoverflow.com/questions/458550
with open(os.path.join('refdata', 'version.py'), 'rt') as f:
    filecontent = f.read()
match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", filecontent, re.M)
if match is not None:
    version = match.group(1)
else:
    raise RuntimeError('unable to find version string in %s.' % (filecontent,))


# Get long project description text from the README.rst file
with open('README.rst', 'rt') as f:
    readme = f.read()


setup(
    name='refdata',
    version=version,
    description='Library for accessing the Reference Data Repository',
    long_description=readme,
    long_description_content_type='text/x-rst',
    keywords='data curation',
    url='https://github.com/VIDA-NYU/reference-data-repository',
    author='Heiko Mueller',
    author_email='heiko.muller@gmail.com',
    license='MIT',
    license_file='LICENSE',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'refdata = refdata.cli.base:cli'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python'
    ]
)
