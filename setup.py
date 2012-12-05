#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

requires = [
    'pyyaml',
    'webob',
    'requests==0.14.2',
    'python3-digest',
    'python3-memcached',
    'pymongo',
    'WTForms',
    'wtforms_json',
    'mailsnake',
    'pil'
]

dep_links = [
    'https://github.com/webitup/py3k-mailsnake/zipball/master#egg=mailsnake',
    'https://github.com/sloonz/pil-py3k/archive/master.zip#egg=pil'
]

setup(
    name='lxxl',
    version=lxxl.__version__,
    description='LxxL Web Services',
    long_description=open('README.rst').read(),
    author='Education Numerique',
    author_email='tech@webitup.fr',
    url='http://education-numerique.github.com/api/',
    packages=find_packages(),
    scripts=[
        'bin/lxxl',
        'bin/lxxl.graph',
        'bin/lxxl.wildbull',
        'bin/lxxl.authentication.admin',
        'bin/lxxl.authentication.front'
    ],
    package_dir={'lxxl': 'lxxl'},
    include_package_data=True,
    install_requires=requires,
    dependency_links=dep_links,
    license=open('LICENSE.md').read()
)

del os.environ['PYTHONDONTWRITEBYTECODE']
