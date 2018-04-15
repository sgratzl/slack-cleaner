# -*- coding: utf-8 -*-

class AndPredicate():
  def __init__(self, fs = None):
    self.fs = fs or []

  def __call__(self, x):
    if not self.fs:
      return True
    return all(f(x) for f in self.fs)

  def __and__(self, other):
    if isinstance(other, AndPredicate):
      self.fs = self.fs + other.fs
      return self
    self.fs.append(other)
    return self

  def __or__(self, other):
    return OrPredicate([self.f, other])


class OrPredicate():
  def __init__(self, fs = None):
    self.fs = fs or []

  def __call__(self, x):
    if not self.fs:
      return False
    return any(f(x) for f in self.fs)

  def __or__(self, other):
    if isinstance(other, OrPredicate):
      self.fs = self.fs + other.fs
      return self
    self.fs.append(other)
    return self

  def __and__(self, other):
    return AndPredicate([self.f, other])


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


def match(pattern, attr = 'name'):
  import re
  regex = re.compile('^' + pattern + '$', re.I)

  def matches(msg_or_file):
    m = regex.search(getattr(msg_or_file, attr))
    return m is not None

  return Predicate(matches)


def name(name):
  return Predicate(lambda msg_or_file: msg_or_file.name == name)


def match_text(pattern):
  return match_pattern(pattenr, 'text')


def match_user(pattern):
  import re
  regex = re.compile('^' + pattern + '$', re.I)
  return Predicate(lambda user: any(regex.search(u or '') for u in [user.id, user.name, user.display_name, user.email, user.real_name]))


def is_member(user):
  return Predicate(lambda channel: user in channel.members)


def by_user(user):
  return Predicate(lambda msg_or_file: msg_or_file.user == user)


def by_users(users):
  s = set(users)
  return Predicate(lambda msg_or_file: msg_or_file.user in s)

