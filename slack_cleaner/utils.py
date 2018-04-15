# -*- coding: utf-8 -*-

import time
import sys
from colorama import init, Fore


init()


class Colors():
  BLUE = Fore.BLUE
  GREEN = Fore.GREEN
  YELLOW = Fore.YELLOW
  RED = Fore.RED
  ENDC = Fore.RESET


class TimeRange():
  def __init__(self, start_time, end_time):
    def parse_ts(t):
      try:
        if len(t) == 8:
          return time.mktime(time.strptime(t, "%Y%m%d"))
        else:
          return time.mktime(time.strptime(t, "%Y%m%d%H%M"))
      except:
        return '0'

    self.start_ts = parse_ts(start_time)
    # Ensure we have the end time since slack will return in different way
    # if no end time supplied
    self.end_ts = parse_ts(end_time)
    if self.end_ts == '0':j
      self.end_ts = str(time.time())

