# -*- coding: utf-8 -*-

import argparse


class Args():
  def __init__(self):
    p = argparse.ArgumentParser(prog='slack-cleaner')

    # Token
    p.add_argument('--token', required=True,
                   help='Slack API token (https://api.slack.com/web)')

    # Log
    p.add_argument('--log', action='store_true',
                   help='Create a log file in the current directory')
    # Quiet
    p.add_argument('--quiet', action='store_true',
                   help='Run quietly, does not log messages deleted')

    # Rate limit
    p.add_argument('--rate', type=float,
                   help='Delay between API calls (in seconds)')

    # Type
    g_type = p.add_mutually_exclusive_group()
    g_type.add_argument('--message', action='store_true',
                        help='Delete messages')
    g_type.add_argument('--file', action='store_true',
                        help='Delete files')

    # Channel, DM or group
    g_chan = p.add_mutually_exclusive_group()
    g_chan.add_argument('--purge',
                        help='Purge messages from all channels')

  g_chan.add_argument('--channel',
                      help='Channel name\'s, e.g., general')
  g_chan.add_argument('--direct',
                      help='Direct message\'s name, e.g., sherry')
  g_chan.add_argument('--group',
                      help='Private group\'s name')
  g_chan.add_argument('--mpdirect',
                      help='Multiparty direct message\'s name, e.g., ' +
                           'sherry,james,johndoe')

  # Conditions
  p.add_argument('--user',
                 help='Delete messages/files from certain user')
  p.add_argument('--botname',
                 help='Delete messages/files from certain bots')
  p.add_argument('--bot', action='store_true',
                 help='Delete messages from bots')
  p.add_argument('--keeppinned', action='store_true',
                 help='exclude pinned messages from deletion')
  p.add_argument('--after',
                 help='Delete messages/files newer than this time ' +
                      '(YYYYMMDD)')
  p.add_argument('--before',
                 help='Delete messages/files older than this time ' +
                      '(YYYYMMDD)')
  p.add_argument('--types',
                 help='Delete files of a certain type, e.g., posts,pdfs')
  p.add_argument('--pattern',
                 help='Delete messages with specified pattern (regex)')

  # Perform or not
  p.add_argument('--perform', action='store_true',
                 help='Perform the task')

  args = p.parse_args()

  if args.message:
    if (args.channel is None and args.direct is None and
            args.group is None and args.mpdirect is None):
      p.error('A channel is required when using --message')

  self.token = args.token

  self.log = args.log

  self.quiet = args.quiet

  self.rate_limit = args.rate

  self.delete_message = args.message
  self.delete_file = args.file

  self.purge_name = args.purge
  self.channel_name = args.channel
  self.direct_name = args.direct
  self.group_name = args.group
  self.mpdirect_name = args.mpdirect

  self.user_name = args.user
  self.botname = args.botname
  self.bot = args.bot
  self.keep_pinned = args.keeppinned
  self.pattern = args.pattern
  self.start_time = args.after
  self.end_time = args.before
  self.types = args.types

  self.perform = args.perform
