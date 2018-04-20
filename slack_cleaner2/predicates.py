# -*- coding: utf-8 -*-
"""
 set of helper predicates to filter messages, channels, and users
 multiple predicates can be combined using & and |
"""


class AndPredicate(object):
  """
   common and predicate
  """
  def __init__(self, children=None):
    self.children = children or []

  def __call__(self, x):
    if not self.children:
      return True
    return all(f(x) for f in self.children)

  def __and__(self, other):
    if isinstance(other, AndPredicate):
      self.children = self.children + other.children
      return self
    self.children.append(other)
    return self

  def __or__(self, other):
    return OrPredicate([self, other])


def and_(predicates):
  """
  combime multiple predicates using and
  """
  return AndPredicate(predicates)


class OrPredicate(object):
  """
   common or predicate
  """
  def __init__(self, children=None):
    self.children = children or []

  def __call__(self, x):
    if not self.children:
      return False
    return any(f(x) for f in self.children)

  def __or__(self, other):
    if isinstance(other, OrPredicate):
      self.children = self.children + other.children
      return self
    self.c.append(other)
    return self

  def __and__(self, other):
    return AndPredicate([self, other])


def or_(predicates):
  """
  combime multiple predicates using or
  """
  return OrPredicate(predicates)


class Predicate(object):
  """
  helper predicate wrapper for having operator support
  """
  def __init__(self, fun):
    self.fun = fun

  def __call__(self, x):
    return self.fun(x)

  def __and__(self, other):
    return AndPredicate([self.fun, other])

  def __or__(self, other):
    return OrPredicate([self.fun, other])


"""
predicate for filtering messages or files that are not pinned
"""
is_not_pinned = Predicate(lambda msg_or_file: not msg_or_file.pinned_to)
"""
prediate for filtering messages or files created by a bot
"""
is_bot = Predicate(lambda msg_or_user: msg_or_user.bot)


def match(pattern, attr='name'):
  """
  predicate for filtering channels which names match the given regex
  """
  import re
  regex = re.compile('^' + pattern + '$', re.I)

  return Predicate(lambda channel: regex.search(getattr(channel, attr)) is not None)


def name(channel_name):
  """
  predicate for filtering channels with the given name
  """
  return Predicate(lambda channel: channel.name == channel_name)


def match_text(pattern):
  """
  predicate for filtering messages which text matches the given regex
  """
  return match(pattern, 'text')


def match_user(pattern):
  """
  predicate for filtering users which match the given regex (id, name, display_name, email, real_name)
  """
  import re
  regex = re.compile('^' + pattern + '$', re.I)
  return Predicate(lambda user: any(
    regex.search(u or '') for u in [user.id, user.name, user.display_name, user.email, user.real_name]))


def is_member(user):
  """
  predicate for filtering channels in which the user is a member of
  """
  return Predicate(lambda channel: user in channel.members)


def by_user(user):
  """
  predicate for filtering messages or files written by the given user
  """
  return Predicate(lambda msg_or_file: msg_or_file.user == user)


def by_users(users):
  """
  predicate for filtering messages or files written by one of the given users
  """
  users = set(users)
  return Predicate(lambda msg_or_file: msg_or_file.user in users)
