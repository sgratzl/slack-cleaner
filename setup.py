import re
import sys
import io
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

pkg_file = io.open("slack_cleaner2/__init__.py", encoding='utf-8').read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", pkg_file))
description = io.open('README.md', encoding='utf-8').read()


class Tox(TestCommand):
  def finalize_options(self):
    TestCommand.finalize_options(self)
    self.test_args = []
    self.test_suite = True

  def run_tests(self):
    #import here, cause outside the eggs aren't loaded
    import tox
    errcode = tox.cmdline(self.test_args)
    sys.exit(errcode)


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
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    tests_require=['tox'],
    test_suite='slack_cleaner2.test.test_slack_cleaner2',
    extras_require={
        'testing': ['tox'],
    },
    cmdclass={'test': Tox},
    install_requires=['slacker', 'colorama'],
    entry_points={
        'console_scripts': [
            'slack-cleaner = slack_cleaner2.cli:run'
        ]
    }
)
