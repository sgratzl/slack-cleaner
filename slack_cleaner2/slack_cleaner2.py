"""
 main module containing the main SlackCleaner class
"""
from requests.sessions import Session
from slacker import Slacker

from .logger import SlackLogger
from .model import SlackUser, SlackChannel, SlackDirectMessage, SlackFile


class SlackCleaner(object):
  """
  base class for cleaning up slack providing access to channels and users
  """

  def __init__(self, token, sleep_for=0, log_to_file=False):
    """
    :param token: the slack token, see README.md for details
    :type token: str
    :param sleep_for: sleep for x (float) seconds between delete calls
    :type sleep_for: float
    :param log_to_file: enable logging to file
    :type log_to_file: bool
    """

    self.log = SlackLogger(log_to_file, sleep_for)
    """
    log instance
    :type SlackLogger
    """

    self.log.debug('start')

    with Session() as session:
      slack = Slacker(token, session=session)
      if hasattr(slack, 'rate_limit_retries'):
        slack.rate_limit_retries = 2

    self.api = slack
    """
    attributes for the underlying slacker instance
    :type Slacker
    """

    self.users = [SlackUser(m, self) for m in _safe_list(slack.users.list(), 'members')]
    """
    list of known users
    :type list of SlackUser
    """
    self.log.debug('collected users %s', self.users)

    self.user = {u.id: u for u in self.users}
    """
    dictionary lookup from user id to SlackUser object
    :type dict of user id to SlackUser
    """

    self.channels = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.channels, self)
      for m in _safe_list(slack.channels.list(), 'channels')
    ]
    """
    list of all channels
    :type list of SlackChannel
    """
    self.log.debug('collected channels %s', self.channels)
    self.groups = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.groups, self)
      for m in _safe_list(slack.groups.list(), 'groups')
    ]
    """
    list of all groups
    :type list of SlackChannel
    """
    self.log.debug('collected groups %s', self.groups)
    self.mpim = [
      SlackChannel(m, [self.user[u] for u in m['members']], slack.mpim, self)
      for m in _safe_list(slack.mpim.list(), 'groups')
    ]
    """
    list of all multi person direct message
    :type list of SlackChannel
    """
    self.log.debug('collected mpim %s', self.mpim)
    self.ims = [
      SlackDirectMessage(m, self.user[m['user']], slack.im, self)
      for m in _safe_list(slack.im.list(), 'ims')
    ]
    """
    list of all instant messages
    :type list of SlackDirectMessage
    """
    self.log.debug('collected ims %s', self.ims)

    # all different types with a similar interface
    self.conversations = self.channels + self.groups + self.mpim + self.ims
    """
    list of all conversations (channels, groups, mpim, ims)
    :type list of SlackChannel
    """

  def files(self, user=None, after=None, before=None, types=None, channel=None):
    """
    list all known slack files for the given parameter as a generator
    :param user: limit to given user id
    :type user: str
    :param after: from
    :type after: int,str,time
    :param before: to
    :type before: int,str,time
    :param types: see types in slack api, default 'all'
    :type types: str
    :param channel: limit to a certain channel id
    :type channel: str
    :return: generator of SlackFile objects
    :rtype SlackFile
    """
    return SlackFile.list(self, user=user, after=after, before=before, types=types, channel=channel)

  def msgs(self, channels=None, after=None, before=None):
    """
    list all known slack messages for the given parameter as a generator
    :param channels: limit to given channels default all conversations
    :type channels: iterable of SlackChannel
    :param after: from
    :type after: int,str,time
    :param before: to
    :type before: int,str,time
    :return: generator of SlackMessage objects
    :rtype SlackMessage
    """
    if not channels:
      channels = self.conversations
    for channel in channels:
      for msg in channel.msgs(after=after, before=before):
        yield msg


def _safe_list(res, attr):
  res = res.body
  if not res['ok'] or not res[attr]:
    return []
  return res[attr]
