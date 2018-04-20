# -*- coding: utf-8 -*-
"""
 model module for absracting channels, messages, and files
"""


class SlackUser(object):
  """
  internal model of a slack user
  """

  def __init__(self, member, slack):
    self.id = member['id']
    self._slack = slack
    self.name = member['name']
    self.real_name = member['profile'].get('real_name')
    self.display_name = member['profile']['display_name']
    self.email = member['profile'].get('email')
    self._entry = member
    self.is_bot = member['is_bot']
    self.is_app_user = member['is_app_user']
    self.bot = self.is_bot or self.is_app_user

  def __str__(self):
    return u'{s.name} ({s.id}) {s.real_name}'.format(s=self)

  def __repr__(self):
    return self.__str__()

  def files(self, after=None, before=None, types=None):
    """
    list all files of the this user
    :param after: from
    :param before: to
    :param types: see slack api doc
    :return:
    """
    return SlackFile.list(self._slack, user=self.id, after=after, before=before, types=types)

  def msgs(self, after=None, before=None):
    """
    list all messages of the this user
    :param after: from
    :param before: to
    :return:
    """
    from .predicates import is_member, by_user
    by_me = by_user(self)
    for msg in self._slack.msgs(filter(is_member(self), self._slack.conversations), after=after, before=before):
      if by_me(msg):
        yield msg


class SlackChannel(object):
  """
  internal model of a slack channel, group, mpim, im
  """

  def __init__(self, entry, members, api, slack):
    self.id = entry['id']
    self.name = entry.get('name', self.id)
    self.members = members
    self.api = api
    self._slack = slack
    self._entry = entry

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.__str__()

  def msgs(self, after=None, before=None):
    """
    retrieve the msgs of all messages as a generator
    :param after: from
    :param before: to
    :return: generator of SlackMessage
    """
    after = _parse_time(after)
    before = _parse_time(before)
    self._slack.log.debug('list msgs of %s (after=%s, before=%s)', self, after, before)
    latest = before
    oldest = after
    has_more = True
    while has_more:
      res = self.api.history(self.id, latest, oldest, count=1000).body
      if not res['ok']:
        return
      messages = res['messages']
      has_more = res['has_more']

      if not messages:
        return

      for msg in messages:
        # Prepare for next page query
        latest = msg['ts']

        user = _find_user(self.members, msg)
        # Delete user messages
        if msg['type'] == 'message':
          yield SlackMessage(msg, user, self, self._slack)

  def replies_to(self, base_msg):
    """
    returns the replies to a given SlackMessage instance
    :param base_msg: message instance to find replies to
    :return:
    """
    res = self.api.replies(self.id, base_msg.ts).body
    if not res['ok']:
      return
    for msg in res['messages']:
      user = _find_user(self.members, msg)
      # Delete user messages
      if msg['type'] == 'message':
        yield SlackMessage(msg, user, self, self._slack)

  def files(self, after=None, before=None, types=None):
    """
    list all files of this channel
    """
    return SlackFile.list(self._slack, channel=self.id, after=after, before=before, types=types)


class SlackDirectMessage(SlackChannel):
  """
  internal model of a slack direct message channel
  """

  def __init__(self, entry, user, api, slack):
    super(SlackDirectMessage, self).__init__(entry, [user], api, slack)
    self.name = user.name
    self.user = user


class SlackMessage(object):
  """
  internal model of a slack message
  """

  def __init__(self, entry, user, channel, slack):
    self.ts = entry['ts']
    self.text = entry['text']
    self._channel = channel
    self._slack = slack
    self.api = slack.api.chat
    self._entry = entry
    self.user = user
    self.bot = entry.get('subtype') == 'bot_message' or 'bot_id' in entry
    self.pinned_to = entry.get('pinned_to', False)

  def delete(self, as_user=False):
    """
    deletes this message
    """
    try:
      # No response is a good response
      self.api.delete(self._channel.id, self.ts, as_user=as_user)
      self._slack.log.deleted(self)
      return None
    except Exception as error:
      self._slack.log.deleted(self, error)
      return error

  def replies(self):
    """
    list all replies of this message
    """
    return self._channel.replies_of(self)

  def __str__(self):
    return u'{c}:{t}'.format(c=self._channel.name, t=self.ts)

  def __repr__(self):
    return self.__str__()


class SlackFile(object):
  """
  internal representation of a slack file
  """

  def __init__(self, entry, user, slack):
    self.id = entry['id']
    self.name = entry['title']
    self.text = self.name
    self.user = user
    self.pinned_to = entry.get('pinned_to', False)
    self._entry = entry
    self._slack = slack
    self.api = slack.api.files

  @staticmethod
  def list(slack, user=None, after=None, before=None, types=None, channel=None):
    """
    list all given files
    """
    after = _parse_time(after)
    before = _parse_time(before)
    page = 1
    has_more = True
    api = slack.api.files
    slack.log.debug('list all files(user=%s, after=%s, before=%s, types=%s, channel=%s', user, after, before, types,
                    channel)

    while has_more:
      res = api.list(user=user, ts_from=after, ts_to=before, type=types, channel=channel, page=page, count=100).body

      if not res['ok']:
        return

      files = res['files']
      current_page = res['paging']['page']
      total_pages = res['paging']['pages']
      has_more = current_page < total_pages
      page = current_page + 1

      for sfile in files:
        yield SlackFile(sfile, slack.user[sfile['user']], slack)

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.__str__()

  def delete(self):
    """
    delete the file itself
    :return:  None if no error occurred
    """
    try:
      # No response is a good response so no error
      self.api.delete(self.id)
      self._slack.log.deleted(self)
      return None
    except Exception as error:
      self._slack.log.deleted(self, error)
      return error


def _parse_time(time_str):
  import time

  if time_str is None:
    return None
  if isinstance(time_str, (int, time)):
    return time_str
  try:
    if len(time_str) == 8:
      return time.mktime(time.strptime(time_str, "%Y%m%d"))
    return time.mktime(time.strptime(time_str, "%Y%m%d%H%M"))
  except ValueError:
    return None


def _find_user(users, msg):
  if 'user' not in msg:
    return None
  userid = msg['user']
  for user in users:
    if user.id == userid:
      return user
  return None
