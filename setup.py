# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
from setuptools import setup, find_packages


if __name__ == '__main__':
    print('Sopel does not correctly load modules installed with setup.py '
          'directly. Please use "pip install .", or add {}/sopel_modules to '
          'core.extra in your config.'.format(
              os.path.dirname(os.path.abspath(__file__))),
          file=sys.stderr)


setup(
    name='sopel_modules.chanlogs',
    version='0.1.0',
    description='A channel logging module for Sopel',
    author='Embolalia',
    author_email='powell.518@gmail.com',
    url='http://github.com/sopel-irc/sopel-chanlogs',
    packages=find_packages('.'),
    namespace_packages=['sopel_modules'],
    include_package_data=True,
    )
