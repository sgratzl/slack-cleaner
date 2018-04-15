# -*- coding: utf-8 -*-
import sys
from colorama import Fore
import logging
import datetime
import pprint


class SlackLoggerRound():
  def __init__(self, name):
    self.deleted = 0
    self.errors = 0
    self.name = name

  def __str__(self):
    return u'{n}: deleted: {d}, errors: {e}'.format(n=self.name, d=self.deleted, e=self.errors)

  def __call__(self, error):
    if error:
      self.errors += 1
    else:
      self.deleted += 1


class SlackLogger():
  def __init__(self, to_file=False, sleep_for = 0):
    self._sleep_for = sleep_for
    self.log = logging.getLogger('slack-cleaner')
    self._pp = pprint.PrettyPrinter(indent=2)
    self._rounds = [SlackLoggerRound('overall')]

    if to_file:
      ts = datetime.now().strftime('%Y%m%d-%H%M%S')
      file_log_handler = logging.FileHandler('slack-cleaner.' + ts + '.log')
      file_log_handler.setLevel(logging.DEBUG)
      self.log.addHandler(file_log_handler)

    # And always display on console
    s = logging.StreamHandler()
    s.setLevel(logging.INFO)
    self.log.addHandler(s)

  def __call__(self, file_or_msg, error=None):
    for round in self._rounds:
      round(error)

    if error:
      sys.stdout.write(Fore.RED + 'x' + Fore.RESET)
      sys.stdout.flush()
      self.log.warning(u'cannot delete entry: %s: %s', file_or_msg, error)
    else:
      sys.stdout.write('.')
      sys.stdout.flush()
      self.og.debug(u'deleted entry: %s', file_or_msg)

    if self._sleep_for > 0:
      from time import sleep
      sleep(self._sleep_for)

  def push(name):
    r = SlackLoggerRound(name)
    self.log.info(u'start deleting: %s', name)
    self._rounds.append(r)
    return r

  def pop():
    r = self._rounds[-1]
    del self._rounds[-1]
    self.log.info(u'stop deleting: %s', r)
    return r

  def __str__(self):
    return unicode(self._rounds[0])
