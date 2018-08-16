import os
from slack_cleaner2 import SlackCleaner, a_while_ago, is_not_pinned
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient()
s = SlackCleaner(os.environ['TOKEN'], 1)

db = client.slack_cleaner
f = is_not_pinned()
before = a_while_ago(months=2)


def archive(c):
  archive = db[c.name]
  _ = archive.create_index([('client_msg_id', 1)], unique=True)
  count = 0
  duplicates = 0
  for msg in filter(f, c.msgs(before=before)):
    if 'client_msg_id' not in msg.json:
      msg.json['client_msg_id'] = str(msg.json['ts'])
    try:
      _ = archive.insert_one(msg.json)
      count += 1
    except DuplicateKeyError:
      duplicates += 1
      pass
  s.log.info('%s archived %d, duplicates: %d', c.name, count, duplicates)


def delete(c):
  with s.log.group(c.name):
    for msg in filter(f, c.msgs(before=before)):
      msg.delete()


for c in s.channels:
  archive(c)

for c in s.groups:
  archive(c)

for c in s.conversations:
  delete(c)
