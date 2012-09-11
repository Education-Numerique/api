#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages
import lxxl

if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist upload')
    sys.exit()

major, minor = sys.version_info[:2]
if major < 3 or minor < 2:
    raise Exception("LxxL requires Python 3.2")

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

requires = []

setup(
    name='lxxl',
    version=lxxl.__version__,
    description='LxxL Web Services',
    long_description=open('README.md').read(),
    author='Education Numerique',
    author_email='tech@webitup.fr',
    url='http://education-numerique.github.com/api/',
    packages=find_packages(),
    package_data={'': ['LICENSE.md']},
    package_dir={'lxxl': 'lxxl'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE.md').read(),
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Affero General \
        Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
    ),
)

del os.environ['PYTHONDONTWRITEBYTECODE']
