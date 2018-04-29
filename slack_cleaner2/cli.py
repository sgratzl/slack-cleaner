# -*- coding: utf-8 -*-
"""
  deprecated cli mimicing old slack cleaner
"""
from colorama import Fore

from .predicates import match_user, match, is_name, and_, by_user, match_text, is_not_pinned, is_bot
from .slack_cleaner2 import SlackCleaner


try:
  from future_builtins import filter
except ImportError:
  pass


def _show_infos(slack):
  """
  show generic information about this slack workspace
  """

  def _print_dict(cat, data):
    msg = u'{}{}:{}'.format(Fore.GREEN, cat, Fore.RESET)
    for k, v in data.items():
      msg += u'\n{} {}'.format(k, v)
    slack.log.info(msg)

  _print_dict(u'users', {u.id: u'{} = {}'.format(u.name, u.real_name) for u in slack.users})

  _print_dict(u'public channels', {u.id: u.name for u in slack.channels})
  _print_dict(u'private channels', {u.id: u.name for u in slack.groups})
  _print_dict(u'instant messages', {u.id: u.name for u in slack.ims})
  _print_dict(u'mulit user direct messsages', {u.id: u.name for u in slack.mpim})


def _resolve_user(slack, args):
  """
  resolves th user to delete messages of
  """
  if args.user == '*':
    return None
  return next(filter(match_user(args.user), slack.users))


def _channels(slack, args):
  """
  resolves channesls to delete messages from
  """
  channels = []

  filter_f = match if args.regex else is_name

  if args.channel:
    channels.extend(filter(filter_f(args.channel), slack.channels))
  if args.group:
    channels.extend(filter(filter_f(args.group), slack.groups))
  if args.direct:
    channels.extend(filter(filter_f(args.direct), slack.ims))
  if args.mpdirect:
    channels.extend(filter(filter_f(args.mpdirect), slack.mpim))

  return channels


def _delete_messages(slack, args):
  """
  delete old messages
  """
  channels = _channels(slack, args)

  pred = []

  user = _resolve_user(slack, args)
  if user:
    pred.append(by_user(user))
  if args.pattern:
    pred.append(match_text(args.pattern))
  if args.keeppinned:
    pred.append(is_not_pinned())
  if args.bot:
    pred.append(is_bot())
  if args.botname:
    pred.append(by_user(next(filter(match_user(args.botname), slack.users))))

  pred = and_(pred)
  total = 0
  for channel in channels:
    with slack.log.group(channel.name):
      for msg in channel.msgs(args.after, args.before):
        if not pred(msg):
          continue
        if args.perform:
          msg.delete(args.as_user)
        total += 1

  slack.log.info(u'summary: %s', slack.log)


def _delete_files(slack, args):
  """
  delete old files
  """
  user = _resolve_user(slack, args)
  channels = _channels(slack, args)

  pred = []

  user = _resolve_user(slack, args)
  if user:
    pred.append(by_user(user))
  if args.pattern:
    pred.append(match(args.pattern))
  if args.keeppinned:
    pred.append(is_not_pinned())
  if args.bot:
    pred.append(is_bot())
  if args.botname:
    pred.append(by_user(next(filter(match_user(args.botname), slack.users))))

  pred = and_(pred)
  total = 0
  for channel in channels:
    with slack.log.group(channel.name):
      for sfile in channel.files(args.after, args.before, args.types):
        if not pred(sfile):
          continue
        if args.perform:
          sfile.delete(args.as_user)
        total += 1

  slack.log.info(u'summary: %s', slack.log)


def _args():
  """
  cli argument parser
  """
  import argparse
  parser = argparse.ArgumentParser(prog='slack-cleaner')
  # Token
  parser.add_argument('--token', required=True,
                      help='Slack API token (https://api.slack.com/web)')

  # Log
  parser.add_argument('--log', action='store_true',
                      help='Create a log file in the current directory')
  # Quiet
  parser.add_argument('--quiet', action='store_true',
                      help='Run quietly, does not log messages deleted')

  # Rate limit
  parser.add_argument('--rate', type=float,
                      help='Delay between API calls (in seconds)')

  # user
  parser.add_argument('--as_user', action='store_true',
                      help='Pass true to delete the message as the authed user. Bot users in this context are considered authed users.')

  # Type
  g_type = parser.add_mutually_exclusive_group()
  g_type.add_argument('--message', action='store_true',
                      help='Delete messages')
  g_type.add_argument('--file', action='store_true',
                      help='Delete files')
  g_type.add_argument('--info', action='store_true',
                      help='Show information')

  parser.add_argument('--regex', action='store_true', help='Interpret channel, direct, group, and mpdirect as regex')
  parser.add_argument('--channel',
                      help='Channel name\'s, e.g., general')
  parser.add_argument('--direct',
                      help='Direct message\'s name, e.g., sherry')
  parser.add_argument('--group',
                      help='Private group\'s name')
  parser.add_argument('--mpdirect',
                      help='Multiparty direct message\'s name, e.g., ' +
                           'sherry,james,johndoe')

  # Conditions
  parser.add_argument('--user',
                      help='Delete messages/files from certain user')
  parser.add_argument('--botname',
                      help='Delete messages/files from certain bots')
  parser.add_argument('--bot', action='store_true',
                      help='Delete messages from bots')

  # Filter
  parser.add_argument('--keeppinned', action='store_true', help='exclude parserinned messages from deletion')
  parser.add_argument('--after', help='Delete messages/files newer than this time (YYYYMMDD)')
  parser.add_argument('--before', help='Delete messages/files older than this time (YYYYMMDD)')
  parser.add_argument('--types', help='Delete files of a certain type, e.g., parserosts,pdfs')
  parser.add_argument('--pattern', help='Delete messages with specified parserattern (regex)')

  # parsererform or not
  parser.add_argument('--perform', action='store_true', help='Perform the task')

  args = parser.parse_args()

  if args.message:
    if (args.channel is None and args.direct is None and args.group is None and args.mpdirect is None):
      parser.error('A channel is required when using --message')

  return args


def main():
  """
  cli main entry
  """
  args = _args()
  slack = SlackCleaner(args.token, args.log, args.rate)

  if args.info:
    _show_infos(slack)
  elif args.message:
    _delete_messages(slack, args)
  elif args.file:
    _delete_files(slack, args)


if __name__ == '__main__':
  import sys

  sys.exit(main())  # pragma: no cover
