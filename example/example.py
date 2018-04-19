from slack_cleaner import *
import os

s = SlackCleaner(os.environ['TOKEN'], false, 1)

with s.log.group('clear bot channels'):
  for msg in s.msgs(filter(match('.*-bots'), s.conversations)):
    msg.delete()

with s.log.group('delete older than 3 months'):
  for msg in s.msgs(filter(is_not_pinned, s.conversations), ts_to=a_while_ago(months=3)):
    msg.delete()

with s.log.group('delete ims older than 1 month'):
  for msg in s.msgs(filter(is_not_pinned, s.ims), ts_to=a_while_ago(months=1)):
    msg.delete()

s.log.summary()
