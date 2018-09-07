#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
  readme = readme_file.read()

with open('HISTORY.rst') as history_file:
  history = history_file.read()

with open('requirements.txt') as req:
  requirements = req.read().split('\n')

info_ns = {}
with open('slack_cleaner2/_info.py') as f:
  exec(f.read(), {}, info_ns)

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
  author=info_ns['__author__'],
  author_email=info_ns['__email__'],
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    "Programming Language :: Python :: 2",
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
  entry_points={
    'console_scripts': [
      'slack-cleaner=slack_cleaner2.cli:main',
    ],
  },
  install_requires=requirements,
  license=info_ns['__license__'],
  long_description=readme + '\n\n' + history,
  include_package_data=True,
  keywords='slack_cleaner2',
  name='slack_cleaner2',
  packages=find_packages(include=['slack_cleaner2']),
  setup_requires=setup_requirements,
  test_suite='tests',
  tests_require=test_requirements,
  url='https://github.com/sgratzl/slack_cleaner2',
  version=info_ns['__version__'],
  zip_safe=False,
)
