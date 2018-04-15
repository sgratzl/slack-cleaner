# -*- coding: utf-8 -*-


def is_not_pinned(msg_or_file):
  return not msg_or_file.pinned_to


def is_bot(msg_or_user):
  return msg_or_user.bot


def match_pattern(pattern, attr = 'name'):
  import re
  regex = re.compile('^' + pattern + '$', re.I)

  def matches(msg_or_file):
    m = regex.search(getattr(msg_or_file, attr))
    return m is not None

  return matches


def equal_to(name):
  return lambda msg_or_file: msg_or_file.name == name


def match_text_pattern(pattern):
  return match_pattern(pattenr, 'text')


def from_user(user):
  return lambda msg_or_file: msg_or_file.user == user


def from_users(users):
  s = set(users)
  return lambda msg_or_file: msg_or_file.user in s


def match_all(predicates):
  return lambda msg_or_file: all(p(msg_or_file) for p in predicates)
