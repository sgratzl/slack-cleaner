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

# So we can print slack's object beautifully
pp = pprint.PrettyPrinter(indent=4)

# Count how many items we deleted
counter = Counter()

# Initial logger
logger = logging.getLogger('slack-cleaner')
logger.setLevel(10)

# Log deleted messages/files if we're gonna actually log the task
if args.log:
  ts = datetime.now().strftime('%Y%m%d-%H%M%S')
  file_log_handler = logging.FileHandler('slack-cleaner.' + ts + '.log')
  logger.addHandler(file_log_handler)

# And always display on console
stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

# Print version information
logger.info('Running slack-cleaner v' + __version__)


def skip_to_delete(m):
  if args.keep_pinned and m.get('pinned_to'):
    return True
  if args.pattern:
    regex = re.compile(args.pattern)
    # name ... file
    # text ... message
    match = regex.search(m.get('text', m.get('name')))
    if match == None:
      return True
  return False


def clean_channel(channel_id, channel_type, time_range, user_id=None, bot=False):
  # Setup time range for query
  oldest = time_range.start_ts
  latest = time_range.end_ts

  _api_end_point = None
  # Set to the right API end point
  if channel_type == 'channel':
    _api_end_point = slack.channels.history
  elif channel_type == 'direct':
    _api_end_point = slack.im.history
  elif channel_type == 'group':
    _api_end_point = slack.groups.history
  elif channel_type == 'mpdirect':
    _api_end_point = slack.mpim.history

  has_more = True
  while has_more:
    res = _api_end_point(channel_id, latest, oldest).body
    if not res['ok']:
      logger.error('Error occurred on Slack\'s API:')
      pp.pprint(res)
      sys.exit(1)

    messages = res['messages']
    has_more = res['has_more']

    if not messages:
      if not args.quiet:
        logger.info('No more messsages')
      break

    for m in messages:
      # Prepare for next page query
      latest = m['ts']

      # Delete user messages
      if m['type'] == 'message':
        # exclude pinned message if asked
        if skip_to_delete(m):
          continue
        # If it's a normal user message
        if m.get('user'):
          # Delete message if user_name matched or `--user=*`
          if m.get('user') == user_id or user_id == -1:
            delete_message_on_channel(channel_id, m)

        # Delete bot messages
        if bot and (m.get('subtype') == 'bot_message' or 'bot_id' in m):
          delete_message_on_channel(channel_id, m)

      # Exceptions
      else:
        logger.error('Weird message')
        pp.pprint(m)

    if args.rate_limit:
      time.sleep(args.rate_limit)


def delete_message_on_channel(channel_id, message):
  def get_user_name(m):
    if m.get('user'):
      _id = m.get('user')
      return user_dict[_id]
    elif m.get('username'):
      return m.get('username')
    else:
      return '_'

  # Actually perform the task
  if args.perform:
    try:
      # No response is a good response
      slack.chat.delete(channel_id, message['ts'], as_user=args.as_user)

      counter.increase()
      if not args.quiet:
        logger.warning(Colors.RED + 'Deleted message -> ' + Colors.ENDC
                       + get_user_name(message)
                       + ' : %s'
                       , message.get('text', ''))
    except Exception as error:
      logger.error(Colors.YELLOW + 'Failed to delete (%s)->' + Colors.ENDC, error)
      pp.pprint(message)

    if args.rate_limit:
      time.sleep(args.rate_limit)

  # Just simulate the task
  else:
    counter.increase()
    if not args.quiet:
      logger.warning(Colors.YELLOW + 'Will delete message -> ' + Colors.ENDC
                     + get_user_name(message)
                     + ' :  %s'
                     , message.get('text', ''))


def remove_files(time_range, user_id=None, types=None, channel_id=None):
  # Setup time range for query
  oldest = time_range.start_ts
  latest = time_range.end_ts
  page = 1

  if user_id == -1:
    user_id = None

  has_more = True
  while has_more:
    res = slack.files.list(user=user_id, ts_from=oldest, ts_to=latest,
                           channel=channel_id,
                           types=types, page=page).body

    if not res['ok']:
      logger.error('Error occurred on Slack\'s API:')
      pp.pprint(res)
      sys.exit(1)

    files = res['files']
    current_page = res['paging']['page']
    total_pages = res['paging']['pages']
    has_more = current_page < total_pages
    page = current_page + 1

    for f in files:
      if skip_to_delete(f):
        continue
      # Delete user file
      delete_file(f)

    if args.rate_limit:
      time.sleep(args.rate_limit)


def delete_file(file):
  # Actually perform the task
  if args.perform:
    try:
      # No response is a good response
      slack.files.delete(file['id'])
      counter.increase()
      if not args.quiet:
        logger.warning(Colors.RED + 'Deleted file -> ' + Colors.ENDC
                      + file.get('title', ''))
    except Exception as error:
      logger.error(Colors.YELLOW + 'Failed to delete (%s) ->' + Colors.ENDC, error)
      pp.pprint(file)

    if args.rate_limit:
      time.sleep(args.rate_limit)

  # Just simulate the task
  elif not args.quiet:
    counter.increase()
    logger.warning(Colors.YELLOW + 'Will delete file -> ' + Colors.ENDC
                   + file.get('title', ''))



def get_user_id_by_name(name):
  for k, v in user_dict.items():
    if v == name:
      return k


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


def resolve_channels():
  _channels = []
  # If channel's name is supplied
  if args.channel_name:
    _channels.extend([(id, name, 'channel') for (id, name) in get_channel_ids_by_pattern(args.channel_name, not args.regex)])

  # If DM's name is supplied
  if args.direct_name:
    _channels.extend([(id, name, 'direct') for (id, name) in get_direct_ids_by_pattern(args.direct_name, not args.regex)])

  # If channel's name is supplied
  if args.group_name:
    _channels.extend([(id, name, 'group') for (id, name) in get_group_ids_by_pattern(args.group_name, not args.regex)])

  # If group DM's name is supplied
  if args.mpdirect_name:
    _channels.extend([(id, name, 'mpdirect') for (id, name) in (get_mpdirect_ids_by_pattern(args.mpdirect_name) if args.regex else get_mpdirect_ids_compatbility(args.mpdirect_name))])

  return _channels


def resolve_user():
  _user_id = None
  # If user's name is also supplied
  if args.user_name:
    # A little bit tricky here, we use -1 to indicates `--user=*`
    if args.user_name == "*":
      _user_id = -1
    else:
      _user_id = get_user_id_by_name(args.user_name)

    if _user_id is None:
      sys.exit('User not found')
  return _user_id


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


def show_infos():
  """
    show user and channel information
  """

  def print_dict(name, d):
    m = Colors.GREEN + name + ':' + Colors.ENDC
    for k, v in d.items():
      m += '\n' + k + ' ' + str(v)
    logger.info(m)

  res = slack.users.list().body
  if res['ok'] and res['members']:
    users = { c['id']: c['name'] + ' = ' + c['profile']['real_name'] for c in res['members']}
  else:
    users = {}
  print_dict('users', users)

  res = slack.channels.list().body
  if res['ok'] and res['channels']:
    channels = { c['id']: c['name'] for c in res['channels']}
  else:
    channels = {}
  print_dict('public channels', channels)

  res = slack.groups.list().body
  if res['ok'] and res['groups']:
    groups = { c['id']: c['name'] for c in res['groups']}
  else:
    groups = {}
  print_dict('private channels', groups)

  res = slack.im.list().body
  if res['ok'] and res['ims']:
    ims = { c['id']: user_dict[c['user']] for c in res['ims']}
  else:
    ims = {}
  print_dict('instant messages', ims)

  res = slack.mpim.list().body
  if res['ok'] and res['groups']:
    mpin = { c['id']: c['name'] for c in res['groups']}
  else:
    mpin = {}
  print_dict('multi user direct messages', mpin)


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
