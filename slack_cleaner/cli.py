from .cleaner import SlackCleaner
from .predicates import match_user, match, name, AndPredicate, by_user, match_text, is_not_pinned, is_bot
from colorama import Fore

def _show_infos(slack, args):
  def print_dict(name, d):
    m = Fore.GREEN + name + ':' + Fore.RESET
    for k, v in d.items():
      m += '\n' + k + ' ' + str(v)
    slack.log.info(m)

  print_dict('users', {u.id: '{} = {]'.format(u.name, u.real_name) for u in slack.users})

  print_dict('public channels', {u.id: u.name for u in slack.channels})
  print_dict('private channels', {u.id: u.name for u in slack.groups})
  print_dict('instant messages', {u.id: u.name for u in slack.ims})
  print_dict('mulit user direct messsages', {u.id: u.name for u in slack.mpim})

def _resolve_user(slack, args):
  if args.user_name == '*':
    return None
  return next(filter(match_user(args.user_name), slack.users))

def _channels(slack, args):
  channels = []

  filter_f = match if args.regex else name

  if args.channel_name:
    channels.extend(filter(filter_f(args.channel_name), slack.channels))
  if args.group_name:
    channels.extend(filter(filter_f(args.group_name), slack.groups))
  if args.direct_name:
    channels.extend(filter(filter_f(args.direct_name), slack.ims))
  if args.mpdirect_name:
    channels.extend(filter(filter_f(args.mpdirect_name), slack.mpim))

  return channels

def _delete_messages(slack, args):
  channels = _channels(slack, args)


  pred = AndPredicate()

  user = _resolve_user(slack, args)
  if user:
    pred.c.append(by_user(user))
  if args.pattern:
    pred.c.append(match_text(args.pattern))
  if args.keep_pinned:
    pred.c.append(is_not_pinned)
  if args.bot:
    pred.c.append(is_bot)
  if args.botname:
    pred.c.append(by_user(next(filter(match_user(args.botname), slack.users))))

  total = 0
  for channel in channels:
    for msg in channel.history(args.start_time, args.end_time):
      if not pred(msg):
        continue
      if args.perform:
        msg.delete(args.as_user)
      total += 1

  slack.log.info('summary: %s', slack.log)

def _delete_files(slack, args):
  user = _resolve_user(slack, args)
  channels = _channels(slack, args)


  pred = AndPredicate()

  user = _resolve_user(slack, args)
  if user:
    pred.c.append(by_user(user))
  if args.pattern:
    pred.c.append(match(args.pattern))
  if args.keep_pinned:
    pred.c.append(is_not_pinned)
  if args.bot:
    pred.c.append(is_bot)
  if args.botname:
    pred.c.append(by_user(next(filter(match_user(args.botname), slack.users))))

  total = 0
  for channel in channels:
    for f in channel.files(args.start_time, args.end_time, args.types):
      if not pred(f):
        continue
      if args.perform:
        f.delete(args.as_user)
      total += 1

  slack.log.info('summary: %s', slack.log)

def run(args):
  slack = SlackCleaner(args.token, args.log, args.rate_limit)

  if args.show_infos:
    _show_infos(slack, args)
  elif args.delete_message:
    _delete_messages(slack, args)
  elif args.delete_file:
    _delete_files(slack, args)
