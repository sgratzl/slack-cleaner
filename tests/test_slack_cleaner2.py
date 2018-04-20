#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `slack_cleaner2` package."""

import pytest
# from slack_cleaner2 import slack_cleaner2
# from slack_cleaner2 import cli


@pytest.fixture
def response():
  """Sample pytest fixture.

  See more at: http://doc.pytest.org/en/latest/fixture.html
  """
  # import requests
  # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
  """Sample pytest test function with the pytest fixture as an argument."""
  # from bs4 import BeautifulSoup
  # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
  """Test the CLI."""
  # TODO
