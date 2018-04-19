import re
import sys

pkg_file = open("slack_cleaner2/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", pkg_file))
description = open('README.md').read()

from setuptools import setup, find_packages

install_requires =

setup(
    name='slack_cleaner2',
    description='Bulk delete messages/files on Slack.',
    packages=find_packages(),
    author=metadata['author'],
    author_email=metadata['authoremail'],
    version=metadata['version'],
    url='https://github.com/kfei/slack-cleaner',
    license="MIT",
    keywords="slack, clean, delete, message, file",
    long_description=description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=['slacker', 'colorama', 'setuptools'],
    entry_points={
        'console_scripts': [
            'slack-cleaner = slack_cleaner2.cli:run'
        ]
    }
)
