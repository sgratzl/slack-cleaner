# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import pprint
import sys
import time
import re
import itertools
from requests.sessions import Session
from slacker import Slacker

from slack_cleaner import __version__
from slack_cleaner.utils import Colors, Counter, TimeRange
from slack_cleaner.args import Args

# Get and parse command line arguments
args = Args()
time_range = TimeRange(args.start_time, args.end_time)

# Print version information
logger.info('Running slack-cleaner v' + __version__)


def clean_channel(channel_id, channel_type, time_range, user_id=None, bot=False):
  # Setup time range for query
  oldest = time_range.start_ts
  latest = time_range.end_ts


def match_by_key(pattern, items, key, equality_match):
  if equality_match:
    return [(item['id'], key(item)) for item in items if pattern == key(item)]
  # ensure it matches the whole string
  regex = re.compile('^' + pattern + '$', re.I)
  return [(item['id'], key(item)) for item in items if regex.match(key(item))]


def get_channel_ids_by_pattern(pattern, equality_match):
  res = slack.channels.list().body
  if not res['ok'] or not res['channels']:
    return []
  return match_by_key(pattern, res['channels'], lambda c: c['name'], equality_match)


def get_direct_ids_by_pattern(pattern, equality_match):
  res = slack.im.list().body
  if not res['ok'] or not res['ims']:
    return []
  ims = res['ims']
  return match_by_key(pattern, res['ims'], lambda i: user_dict[i['user']], equality_match)


def get_group_ids_by_pattern(pattern, equality_match):
  res = slack.groups.list().body
  if not res['ok'] or not res['groups']:
    return []
  return match_by_key(pattern, res['groups'], lambda c: c['name'], equality_match)


def get_mpdirect_ids_by_pattern(pattern):
  res = slack.mpim.list().body
  if not res['ok'] or not res['groups']:
    return []
  mpims = res['groups']

  regex = re.compile('^' + pattern + '$', re.I)
  def matches(members):
    names = [user_dict[m] for m in mpim['members']]
    # has to match at least one permutation of the members
    for permutation in itertools.permutations(names):
      if (regex.match(','.join(permutation))):
        return True
    return False

  return [(mpim['id'], ','.join(user_dict[m] for m in mpim['members'])) for mpim in mpims if matches(mpim['members'])]


def get_mpdirect_ids_compatbility(name):
  res = slack.mpim.list().body
  if not res['ok'] or not res['groups']:
    return []
  mpims = res['groups']

  # create set of user ids
  members = set([get_user_id_by_name(x) for x in name.split(',')])

  for mpim in mpims:
    # match the mpdirect user ids
    if set(mpim['members']) == members:
      return [(mpim['id'], ','.join(user_dict[m] for m in mpim['members']))]
  return []


def message_cleaner():
  _channels = resolve_channels()
  _user_id = resolve_user()

  if not _channels:
    sys.exit('Channel, direct message or private group not found')

  for (channel_id, channel_name, channel_type) in _channels:
    logger.info('Deleting messages from %s %s', channel_type, channel_name)
    # Delete messages on certain channel
    clean_channel(channel_id, channel_type, time_range, user_id=_user_id, bot=args.bot)


def file_cleaner():
  _types = args.types if args.types else None
  _channels = resolve_channels()
  _user_id = resolve_user()

  if not _channels:
    logger.info('Deleting all matching files')
    remove_files(time_range, user_id=_user_id, types=_types, channel_id=None)


  for (channel_id, channel_name, channel_type) in _channels:
    logger.info('Deleting files from %s %s', channel_type, channel_name)
    remove_files(time_range, user_id=_user_id, types=_types, channel_id=channel_id)



def main():
  if args.show_infos:
    show_infos()

  # Dispatch
  if args.delete_message:
    message_cleaner()
  elif args.delete_file:
    file_cleaner()

  # Compose result string
  result = Colors.GREEN + str(counter.total) + Colors.ENDC
  if args.delete_message:
    result += ' message(s)'
  elif args.delete_file:
    result += ' file(s)'

  if not args.perform:
    result += ' will be cleaned.'
  else:
    result += ' cleaned.'

  # Print result
  logger.info('\n' + result + '\n')

  if not args.perform:
    logger.info('Now you can re-run this program with `--perform`' +
                ' to actually perform the task.' + '\n')


if __name__ == '__main__':
  main()
