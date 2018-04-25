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

  def __call__(self, obj):
    if not self.children:
      return True
    return all(f(obj) for f in self.children)

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
  combines multiple predicates using a logical and

  :param predicates: the predicates to combine
  :type predicates: [Predicate]
  :return: a new predicate
  :rtype: AndPredicate
  """
  return AndPredicate(predicates)


class OrPredicate(object):
  """
   common or predicate
  """

  def __init__(self, children=None):
    self.children = children or []

  def __call__(self, obj):
    if not self.children:
      return False
    return any(f(obj) for f in self.children)

  def __or__(self, other):
    if isinstance(other, OrPredicate):
      self.children = self.children + other.children
      return self
    self.children.append(other)
    return self

  def __and__(self, other):
    return AndPredicate([self, other])


def or_(predicates):
  """
  combines multiple predicates using a logical or

  :param predicates: the predicates to combine
  :type predicates: [Predicate]
  :return: a new predicate
  :rtype: OrPredicate
  """
  return OrPredicate(predicates)


class Predicate(object):
  """
  helper predicate wrapper for having operator support
  """

  def __init__(self, fun):
    """
    :param fun: function to evaluate
    """
    self.fun = fun

  def __call__(self, obj):
    return self.fun(obj)

  def __and__(self, other):
    return AndPredicate([self.fun, other])

  def __or__(self, other):
    return OrPredicate([self.fun, other])


def is_not_pinned():
  """
  predicate for filtering messages or files that are not pinned
  """
  return Predicate(lambda msg_or_file: not msg_or_file.pinned_to)


def is_bot():
  """
  predicate for filtering messages or files created by a bot
  """
  return Predicate(lambda msg_or_user: msg_or_user.bot)


def match(pattern, attr='name'):
  """
  predicate for filtering channels which names match the given regex

  :param pattern: regex pattern to match
  :type pattern: str
  :param attr: attribute to check of the object
  :type attr: str
  :return: Predicate
  :rtype: Predicate
  """
  import re
  regex = re.compile('^' + pattern + '$', re.I)

  return Predicate(lambda channel: regex.search(getattr(channel, attr)) is not None)


def is_name(channel_name):
  """
  predicate for filtering channels with the given name

  :param name: string to match
  :type name: str
  :return: Predicate
  :rtype: Predicate
  """
  return Predicate(lambda channel: channel.name == channel_name)


def match_text(pattern):
  """
  predicate for filtering messages which text matches the given regex

  :param pattern: regex to match
  :type pattern: str
  :return: Predicate
  :rtype: Predicate
  """
  return match(pattern, 'text')


def match_user(pattern):
  """
  predicate for filtering users which match the given regex (any of id, name, display_name, email, real_name)

  :param pattern: regex to match
  :type pattern: str
  :return: Predicate
  :rtype: Predicate
  """
  import re
  regex = re.compile('^' + pattern + '$', re.I)
  return Predicate(lambda user: any(
    regex.search(u or '') for u in [user.id, user.name, user.display_name, user.email, user.real_name]))


def is_member(user):
  """
  predicate for filtering channels in which the given user is a member of

  :param user: the user to check
  :type user: SlackUser
  :return: Predicate
  :rtype: Predicate
  """
  return Predicate(lambda channel: user in channel.members)


def by_user(user):
  """
  predicate for filtering messages or files written by the given user

  :param users: the users to check
  :type user: [SlackUser]
  :return: Predicate
  :rtype: Predicate
  """
  return Predicate(lambda msg_or_file: msg_or_file.user == user)


def by_users(users):
  """
  predicate for filtering messages or files written by one of the given users

  :param users: the users to check
  :type user: [SlackUser]
  :return: Predicate
  :rtype: Predicate
  """
  users = set(users)
  return Predicate(lambda msg_or_file: msg_or_file.user in users)
