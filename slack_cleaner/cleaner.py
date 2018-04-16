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
    return SlackFile.list(self, user=user, ts_from=ts_from, ts_to=ts_to, types=types, channel=channel)


def _safe_list(res, attr):
  res = res.body
  if not res['ok'] or not res[attr]:
    return []
  return res[attr]
