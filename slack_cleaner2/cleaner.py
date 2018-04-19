from requests.sessions import Session
from slacker import Slacker

from .model import SlackUser, SlackChannel, SlackDirectMessage, SlackFile
from .logger import SlackLogger


class SlackCleaner:
  """
  base class for cleaning up slack providing access to channels and users
  """

  def __init__(self, token, log_to_file=False, sleep_for=0):
    """
    :param token: the slack token, see README.md for details
    :param log_to_file: enable loggint to file
    :param sleep_for: sleep for x (float) seconds between delete calls
    """

    self.log = SlackLogger(log_to_file, sleep_for)

    self.log.debug('start')

    with Session() as session:
      slack = self.api = Slacker(token, session=session)
      if hasattr(slack, 'rate_limit_retries'):
        slack.rate_limit_retries = 2


    self.users = [SlackUser(m, self) for m in _safe_list(slack.users.list(), 'members')]
    self.log.debug('collected users %s', self.users)

    self.user = {u.id: u for u in self.users}

    self.channels = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.channels, self)
      for m in _safe_list(slack.channels.list(), 'channels')
    ]
    self.log.debug('collected channels %s', self.channels)
    self.groups = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.groups, self)
      for m in _safe_list(slack.groups.list(), 'groups')
    ]
    self.log.debug('collected groups %s', self.groups)
    self.mpim = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.mpim, self)
      for m in _safe_list(slack.mpim.list(), 'groups')
    ]
    self.log.debug('collected mpim %s', self.mpim)
    self.ims = [
      SlackDirectMessage(m, self.user[m['user']], slack.im, self)
      for m in _safe_list(slack.im.list(), 'ims')
    ]
    self.log.debug('collected ims %s', self.ims)

    # all different types with a similar interface
    self.conversations = self.channels + self.groups + self.mpim + self.ims

  def files(self, user=None, ts_from=None, ts_to=None, types=None, channel=None):
    """
    list all known slack files for the given parameter as a generator
    :param user: limit to given user id
    :param ts_from: from
    :param ts_to: to
    :param types: see types in slack api, default 'all'
    :param channel: limit to a certain channel id
    :return: generator of SlackFile objects
    """
    return SlackFile.list(self, user=user, ts_from=ts_from, ts_to=ts_to, types=types, channel=channel)

  def msgs(self, channels=None, ts_from=None, ts_to=None):
    """
    list all known slack messages for the given parameter as a generator
    :param channels: limit to given channels default all conversations
    :param ts_from: from
    :param ts_to: to
    :return: generator of SlackMessage objects
    """
    if not channels:
      channels = self.conversations
    for c in channels:
      for msg in c.msgs(ts_from=ts_from, ts_to=ts_to):
        yield msg



def _safe_list(res, attr):
  res = res.body
  if not res['ok'] or not res[attr]:
    return []
  return res[attr]
