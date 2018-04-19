# -*- coding: utf-8 -*-

class AndPredicate:
  def __init__(self, c=None):
    self.c = c or []

  def __call__(self, x):
    if not self.c:
      return True
    return all(f(x) for f in self.c)

  def __and__(self, other):
    if isinstance(other, AndPredicate):
      self.c = self.c + other.c
      return self
    self.c.append(other)
    return self

  def __or__(self, other):
    return OrPredicate([self, other])


class OrPredicate:
  def __init__(self, c=None):
    self.c = c or []

  def __call__(self, x):
    if not self.c:
      return False
    return any(f(x) for f in self.c)

  def __or__(self, other):
    if isinstance(other, OrPredicate):
      self.c = self.c + other.c
      return self
    self.c.append(other)
    return self

  def __and__(self, other):
    return AndPredicate([self, other])


class Predicate():
  def __init__(self, f):
    self.f = f

  def __call__(self, x):
    return self.f(x)

  def __and__(self, other):
    return AndPredicate([self.f, other])

  def __or__(self, other):
    return OrPredicate([self.f, other])


is_not_pinned = Predicate(lambda msg_or_file: not msg_or_file.pinned_to)
is_bot = Predicate(lambda msg_or_user: msg_or_user.bot)


def match(pattern, attr='name'):
  import re
  regex = re.compile('^' + pattern + '$', re.I)

  def matches(msg_or_file):
    m = regex.search(getattr(msg_or_file, attr))
    return m is not None

  return Predicate(matches)


def name(name):
  return Predicate(lambda msg_or_file: msg_or_file.name == name)


def match_text(pattern):
  return match(pattern, 'text')


def match_user(pattern):
  import re
  regex = re.compile('^' + pattern + '$', re.I)
  return Predicate(lambda user: any(
    regex.search(u or '') for u in [user.id, user.name, user.display_name, user.email, user.real_name]))


def is_member(user):
  return Predicate(lambda channel: user in channel.members)


def by_user(user):
  return Predicate(lambda msg_or_file: msg_or_file.user == user)


def by_users(users):
  s = set(users)
  return Predicate(lambda msg_or_file: msg_or_file.user in s)
