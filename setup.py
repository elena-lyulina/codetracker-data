# Copyright (c) 2020 Anastasiia Birillo, Elena Lyulina

import sys

from setuptools import setup, find_packages

import src
from src.test.util import get_level_by_param


with open('README.md') as readme_file:
    readme = readme_file.read()

# Todo: find a better way for it
args = sys.argv
test_level_param = '--test_level'

if test_level_param in args:
    test_level_index = args.index(test_level_param)
    if test_level_index + 1 >= len(args):
        raise ValueError(f'The param {test_level_param} does not have a value, but it is necessarily!')
    test_level_key = sys.argv[test_level_index + 1]
    src.test.util.CURRENT_TEST_LEVEL = get_level_by_param(test_level_key)
    sys.argv.remove(test_level_param)
    sys.argv.remove(test_level_key)

setup(name='codetracker-data',
      # version='1.0.0',
      description='Data preprocessing, hint generation algorithm',
      url='https://github.com/elena-lyulina/codetracker-data',
      author='Anastasiia Birillo, Elena Lyulina',
      long_description_content_type='text/markdown',
      long_description=readme,
      license='MIT',
      packages=find_packages(),
      python_requires='>=3'
      )
