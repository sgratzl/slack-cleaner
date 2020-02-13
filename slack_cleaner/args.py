# -*- coding: utf-8 -*-

import argparse
import os
from slack_cleaner import __version__

class Args():
  def __init__(self):
    p = argparse.ArgumentParser(prog='slack-cleaner')

    # Token
    env_token = os.environ.get('SLACK_TOKEN', None)
    p.add_argument('--token', required=not env_token,
                   default=env_token,
                   help='Slack API token (https://api.slack.com/web) or SLACK_TOKEN env var')

    # Log
    p.add_argument('--log', action='store_true',
                   help='Create a log file in the current directory')
    # Quiet
    p.add_argument('--quiet', action='store_true',
                   help='Run quietly, does not log messages deleted')

    # Rate limit
    p.add_argument('--rate', type=float,
                   help='Delay between API calls (in seconds)')

    # user
    p.add_argument('--as_user', action='store_true',
                   help='Pass true to delete the message as the authed user. Bot users in this context are considered authed users.')

    # proxy
    p.add_argument('--proxy',
                   help='Proxy server url:port')
    p.add_argument('--verify',
                   help='Verify option for Session (http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification)')

    # Type
    g_type = p.add_mutually_exclusive_group()
    g_type.add_argument('--message', action='store_true',
                        help='Delete messages')
    g_type.add_argument('--file', action='store_true',
                        help='Delete files')
    g_type.add_argument('--info', action='store_true',
                        help='Show information')

    p.add_argument('--regex', action='store_true', help='Interpret channel, direct, group, and mpdirect as regex')
    p.add_argument('--channel',
                        help='Channel name\'s, e.g., general')
    p.add_argument('--direct',
                        help='Direct message\'s name, e.g., sherry')
    p.add_argument('--group',
                        help='Private group\'s name')
    p.add_argument('--mpdirect',
                        help='Multiparty direct message\'s name, e.g., ' +
                             'sherry,james,johndoe')

    # Conditions
    p.add_argument('--user',
                   help='Delete messages/files from certain user')
    p.add_argument('--botname',
                   help='Delete messages/files from certain bots. Implies --bot')
    p.add_argument('--bot', action='store_true',
                   help='Delete messages from bots')

    # Filter
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
                   help='Delete messages/files with specified pattern or when one of their attachments matches (regex)')

    # Our Version
    p.add_argument('--version', action='version', version='Version ' + __version__,
                   help='Print Program Version')

    # Perform or not
    p.add_argument('--perform', action='store_true',
                   help='Perform the task')

    args = p.parse_args()

    if args.message:
      if (args.channel is None and args.direct is None and
              args.group is None and args.mpdirect is None):
        p.error('A channel is required when using --message')

    self.token = args.token

    self.show_infos = args.info

    self.log = args.log
    self.quiet = args.quiet
    self.rate_limit = args.rate
    self.as_user = args.as_user

    self.proxy = args.proxy
    self.verify = args.verify

    self.delete_message = args.message
    self.delete_file = args.file

    self.regex = args.regex
    self.channel_name = args.channel
    self.direct_name = args.direct
    self.group_name = args.group
    self.mpdirect_name = args.mpdirect

    self.user_name = args.user
    self.botname = args.botname
    self.bot = args.bot or (args.botname is not None) # --botname implies --bot
    self.keep_pinned = args.keeppinned
    self.pattern = args.pattern
    self.start_time = args.after
    self.end_time = args.before
    self.types = args.types

    self.perform = args.perform
