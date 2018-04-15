
from requests.sessions import Session
from slacker import Slacker
from .model import SlackUser, SlackChannel, SlackDirectMessage, SlackFile


class SlackCleaner():
  def __init__(self, token):

    with Session() as session:
      slack = self._slack = Slacker(token, session=session)
      if hasattr(slack, 'rate_limit_retries'):
        slack.rate_limit_retries = 2

    self.users = [SlackUser(m, slack) for m in _safe_list(slack.users.list(), 'members')]

    self._user_lookup = {u.id : u for u in self.users}

    self.channels = [
      SlackChannel(m, [self._user_lookup[u] for u in m['members']], slack.channels, slack)
      for m in _safe_list(slack.channels.list(), 'channels')
    ]
    self.groups = [
      SlackChannel(m, [self._user_lookup[u] for u in m['members']], slack.groups, slack)
      for m in _safe_list(slack.groups.list(), 'groups')
    ]
    self.mpim = [
      SlackChannel(m, [self._user_lookup[u] for u in m['members']], slack.mpim, slack)
      for m in _safe_list(slack.mpim.list(), 'groups')
    ]
    self.ims = [SlackDirectMessage(m, self._user_lookup[m['user']], slack.im, slack) for m in _safe_list(slack.im.list(), 'ims')]

    # all different types with a similar interface
    self.conversations = self.channels + self.groups + self.mpim + self.ims

  def files(self):
    return SlackFile.list(self._slack.files)


def _safe_list(res, attr):
  res = res.body
  if not res['ok'] or not res[attr]:
    return []
  return res[attr]
