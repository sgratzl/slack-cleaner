from dateutil import relativedelta
from datetime import datetime
import time


def a_while_ago(years=0, months=0, days=0, leapdays=0, weeks=0,
                hours=0, minutes=0, seconds=0, microseconds=0):
  now = datetime.now()
  ago = (now - relativedelta.relativedelta(years=years, months=months, days=days, leapdays=leapdays, weeks=weeks,
                                           hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds))

  unixtime = time.mktime(ago.timetuple())
  return unixtime
