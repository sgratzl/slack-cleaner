
from requests.sessions import Session
from slacker import Slacker
from .model import SlackUser, SlackChannel, SlackDirectMessage, SlackFile


class SlackCleaner():
  def __init__(self, token):

    with Session() as session:
      slack = self.api = Slacker(token, session=session)
      if hasattr(slack, 'rate_limit_retries'):
        slack.rate_limit_retries = 2

    self.users = [SlackUser(m, self) for m in _safe_list(slack.users.list(), 'members')]

    self.user = {u.id : u for u in self.users}

    self.channels = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.channels, self)
      for m in _safe_list(slack.channels.list(), 'channels')
    ]
    self.groups = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.groups, self)
      for m in _safe_list(slack.groups.list(), 'groups')
    ]
    self.mpim = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.mpim, self)
      for m in _safe_list(slack.mpim.list(), 'groups')
    ]
    self.ims = [SlackDirectMessage(m, self.user[m['user']], slack.im, self) for m in _safe_list(slack.im.list(), 'ims')]

    # all different types with a similar interface
    self.conversations = self.channels + self.groups + self.mpim + self.ims

  def files(self, **kwargs):
    return SlackFile.list(self._slack.files, **kwargs)


def _safe_list(res, attr):
  res = res.body
  if not res['ok'] or not res[attr]:
    return []
  return res[attr]
