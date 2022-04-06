# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
from setuptools import setup, find_packages


if __name__ == '__main__':
    print('Sopel does not correctly load plugins installed with setup.py '
          'directly. Please use "pip install .", or add {}/sopel_modules to '
          'core.extra in your config.'.format(
              os.path.dirname(os.path.abspath(__file__))),
          file=sys.stderr)


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sopel_modules.chanlogs',
    version='0.2.2',
    description='A channel logging plugin for Sopel',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='dgw',
    author_email='dgw@technobabbl.es',
    url='https://github.com/sopel-irc/sopel-chanlogs',
    packages=find_packages('.'),
    install_requires=['sopel>=7.0,<8'],
    namespace_packages=['sopel_modules'],
    include_package_data=True,
    )
