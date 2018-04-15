import sys
from colorama import Fore
import logging
import datetime
import pprint

def SlackLogger():
  def __init__(self, to_file=False, sleep_for = 0):
    self._sleep_for = sleep_for
    self._logger = logging.getLogger('slack-cleaner')
    self._pp = pprint.PrettyPrinter(indent=2)
    self._deleted = 0
    self._errors = []

    if to_file:
      ts = datetime.now().strftime('%Y%m%d-%H%M%S')
      file_log_handler = logging.FileHandler('slack-cleaner.' + ts + '.log')
      file_log_handler.setLevel(logging.DEBUG)
      self._logger.addHandler(file_log_handler)

    # And always display on console
    s = logging.StreamHandler()
    s.setLevel(logging.INFO)
    logger.addHandler(s)

  def __call__(self, file_or_msg, error):
    if error:
      self._error.append(file_or_msg)
      sys.stdout.write(Fore.RED + 'x' + Fore.RESET)
      sys.stdout.flush()
      self._logger.warning('cannot delete entry: %s: %s', file_or_msg, error)
    else:
      self._deleted += 1
      sys.stdout.write('.')
      sys.stdout.flush()
      self._logger.debug('deleted entry: %s', file_or_msg)

    if self._sleep_for > 0:
      from time import sleep
      sleep(self._sleep_for)

  def __str__(self):
    return 'deleted: {d}, errors: {e}'.format(d=self._deleted, e=len(self._errors)
