#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Sneakernet filesync',
    'author': 'Rick van de Loo',
    'url': 'https://github.com/vdloo/messor',
    'author_email': 'rickvandeloo@gmail.com',
    'version': '0.1',
    'install_requires': [],
    'packages': ['messor'],
    'name': 'messor'
}

setup(**config)
