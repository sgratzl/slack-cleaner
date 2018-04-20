import os
from itertools import ifilter
from slack_cleaner2 import *


s = SlackCleaner(os.environ['TOKEN'], 1)

with s.log.group('clear bot channels'):
  for msg in s.msgs(ifilter(match('.*-bots'), s.conversations)):
    msg.delete()

#with s.log.group('delete older than 3 months'):
#  for msg in ifilter(is_not_pinned(), s.msgs(before=a_while_ago(months=3))):
#    msg.delete()

#with s.log.group('delete ims older than 1 month'):
#  for msg in ifilter(is_not_pinned(), s.msgs(s.ims, before=a_while_ago(months=1))):
#    msg.delete()

s.log.summary()
