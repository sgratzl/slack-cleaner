# -*- coding: utf-8 -*-
"""
 model module for absracting channels, messages, and files
"""


class SlackUser(object):
  """
  internal model of a slack user
  """

  id = None  # type: str
  """
  user id
  """

  name = None  # tyoe: str
  """
  user name
  """

  real_name = None  # tpye: str
  """
  user real name
  """

  display_name = None  # type: str
  """
  user display name
  """

  email = None  # type: str
  """
  user email address
  """

  is_bot = False  # type: bool
  """
  is it a bot user
  """

  is_app_user = False  # type: bool
  """
  is it an app user
  """

  bot = False  # type: bool
  """
  is it a bot or app user
  """

  json = None  # type: dict
  """
  the underlying slack response as json
  """

  def __init__(self, entry, slack):
    """
    :param entry: json dict entry as returned by slack api
    :type entry: dict
    :param slack: slack cleaner instance
    :type slack: SlackCleaner
    """
    self.id = entry['id']
    self._slack = slack
    self.name = entry['name']
    self.real_name = entry['profile'].get('real_name')
    self.display_name = entry['profile']['display_name']
    self.email = entry['profile'].get('email')
    self.json = entry
    self.is_bot = entry['is_bot']
    self.is_app_user = entry['is_app_user']
    self.bot = self.is_bot or self.is_app_user

  def __str__(self):
    return u'{s.name} ({s.id}) {s.real_name}'.format(s=self)

  def __repr__(self):
    return self.__str__()

  def files(self, after=None, before=None, types=None):
    """
    list all files of this user

    :param after: limit to entries after the given timestamp
    :type after: int,str,time
    :param before: limit to entries before the given timestamp
    :type before: int,str,time
    :param types: see slack api, one or multiple of all,spaces,snippets,images,gdocs,zips,pdfs
    :type types: str
    :return: generator of SlackFile objects
    :rtype: SlackFile
    """
    return SlackFile.list(self._slack, user=self.id, after=after, before=before, types=types)

  def msgs(self, after=None, before=None):
    """
    list all messages of this user

    :param after: limit to entries after the given timestamp
    :type after: int,str,time
    :param before: limit to entries before the given timestamp
    :type before: int,str,time
    :return: generator of SlackMessage objects
    :rtype: SlackMessage
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

  id = None  # type: str
  """
  channel id
  """

  name = None  # type: str
  """
  channel name
  """

  members = []  # type: [SlackUser]
  """
  list of members
  """

  api = None
  """
  Slacker sub api
  """

  json = None  # type: dict
  """
  the underlying slack response as json
  """

  def __init__(self, entry, members, api, slack):
    """
    :param entry: json dict entry as returned by slack api
    :type entry: dict
    :param members: list of members
    :type members: [SlackUser]
    :param api: Slacker sub api
    :param slack: slack cleaner instance
    :type slack: SlackCleaner
    """

    self.id = entry['id']
    self.name = entry.get('name', self.id)
    self.members = members
    self.api = api
    self._slack = slack
    self.json = entry

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.__str__()

  def msgs(self, after=None, before=None, asc=False):
    """
    retrieve all messages as a generator

    :param after: limit to entries after the given timestamp
    :type after: int,str,time
    :param before: limit to entries before the given timestamp
    :type before: int,str,time
    :param asc: retunging a batch of messages in ascending order
    :type asc: boolean
    :return: generator of SlackMessage objects
    :rtype: SlackMessage
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

      # earliest message
      # Prepare for next page query
      latest = messages[-1]

      for msg in reversed(messages) if asc else messages:
        user = _find_user(self._slack.user, msg)
        # Delete user messages
        if msg['type'] == 'message':
          yield SlackMessage(msg, user, self, self._slack)

  def replies_to(self, base_msg):
    """
    returns the replies to a given SlackMessage instance

    :param base_msg: message instance to find replies to
    :type base_msg: SlackMessage
    :return: generator of SlackMessage replies
    :rtype: SlackMessage
    """
    res = self.api.replies(self.id, base_msg.ts).body
    if not res['ok']:
      return
    for msg in res['messages']:
      user = _find_user(self._slack.user, msg)
      # Delete user messages
      if msg['type'] == 'message':
        yield SlackMessage(msg, user, self, self._slack)

  def files(self, after=None, before=None, types=None):
    """
    list all files of this channel

    :param after: limit to entries after the given timestamp
    :type after: int,str,time
    :param before: limit to entries before the given timestamp
    :type before: int,str,time
    :param types: see slack api, one or multiple of all,spaces,snippets,images,gdocs,zips,pdfs
    :type types: str
    :return: generator of SlackFile objects
    :rtype: SlackFile
    """
    return SlackFile.list(self._slack, channel=self.id, after=after, before=before, types=types)


class SlackDirectMessage(SlackChannel):
  """
  internal model of a slack direct message channel
  """

  user = None  # type: SlackUser
  """
  user talking to
  """

  def __init__(self, entry, user, api, slack):
    """
    :param entry: json dict entry as returned by slack api
    :type entry: dict
    :param user: user talking to
    :type user: SlackUser
    :param api: Slacker sub api
    :param slack: slack cleaner instance
    :type slack: SlackCleaner
    """

    super(SlackDirectMessage, self).__init__(entry, [user], api, slack)
    self.name = user.name
    self.user = user


class SlackMessage(object):
  """
  internal model of a slack message
  """

  ts = None  # type: float
  """
  message timestamp
  """

  text = None  # type: str
  """
  message text
  """

  api = None
  """
  slacker sub api
  """

  user = None  # type: SlackUser
  """
  user sending the messsage
  """

  bot = False  # type: bool
  """
  is the message written by a bot
  """

  pinned_to = False  # type: bool
  """
  is the message pinned
  """

  json = None  # type: dict
  """
  the underlying slack response as json
  """

  def __init__(self, entry, user, channel, slack):
    """
    :param entry: json dict entry as returned by slack api
    :type entry: dict
    :param user: user wrote this message
    :type user: SlackUser
    :param channel: channels this message is written in
    :type channel: SlackChannel
    :param slack: slack cleaner instance
    :type slack: SlackCleaner
    """

    self.ts = float(entry['ts'])
    self.text = entry['text']
    self._channel = channel
    self._slack = slack
    self.api = slack.api.chat
    self.json = entry
    self.user = user
    self.bot = entry.get('subtype') == 'bot_message' or 'bot_id' in entry
    self.pinned_to = entry.get('pinned_to', False)

  def delete(self, as_user=False):
    """
    deletes this message

    :param as_user: trigger the delete operation as the user identified by the token
    :type as_user: bool
    :return: None if successful else error
    :rtype: Exception
    """
    try:
      # No response is a good response
      self.api.delete(self._channel.id, self.json['ts'], as_user=as_user)
      self._slack.log.deleted(self)
      return None
    except Exception as error:
      self._slack.log.deleted(self, error)
      return error

  def replies(self):
    """
    list all replies of this message

    :return: generator of SlackMessage objects
    :rtype: SlackMessage
    """
    return self._channel.replies_to(self)

  def __str__(self):
    return u'{c}:{t} ({u}): {s}'.format(c=self._channel.name, t=self.ts, u='bot' if self.bot else self.user, s=self.text[0:20] if len(self.text) > 20 else self.text)

  def __repr__(self):
    return self.__str__()


class SlackFile(object):
  """
  internal representation of a slack file
  """

  id = None  # type: str
  """
  file id
  """

  name = None  # type: str
  """
  file name
  """

  title = None  # type: str
  """
  file title
  """

  api = None
  """
  slacker sub api
  """

  user = None  # type: SlackUser
  """
  user created this file
  """

  pinned_to = False  # type: bool
  """
  is the file pinned
  """

  mimetype = None  # type: str
  """
  the file mime type
  """

  size = None  # type: int
  """
  the file size
  """

  is_public = False  # type: bool
  """
  is the file public
  """

  json = None  # type: dict
  """
  the underlying slack response as json
  """

  def __init__(self, entry, user, slack):
    """
    :param entry: json dict entry as returned by slack api
    :type entry: dict
    :param user: user created this file
    :param slack: slack cleaner instance
    :type slack: SlackCleaner
    """
    self.id = entry['id']
    self.name = entry['name']
    self.title = entry['title']
    self.user = user
    self.pinned_to = entry.get('pinned_to', False)
    self.mimetype = entry.get('mimetype')
    self.size = entry['size']
    self.is_public = entry['is_public']

    self.json = entry
    self._slack = slack
    self.api = slack.api.files

  @staticmethod
  def list(slack, user=None, after=None, before=None, types=None, channel=None):
    """
    list all given files

    :param user: user id to limit search
    :type user: str,SlackUser
    :param after: limit to entries after the given timestamp
    :type after: int,str,time
    :param before: limit to entries before the given timestamp
    :type before: int,str,time
    :param channel: channel to limit search
    :type channel: str,SlackChannel
    :param types: see slack api, one or multiple of all,spaces,snippets,images,gdocs,zips,pdfs
    :type types: str
    :return: generator of SlackFile objects
    :rtype: SlackFile
    """

    after = _parse_time(after)
    before = _parse_time(before)
    if isinstance(user, SlackUser):
      user = user.id
    if isinstance(channel, SlackChannel):
      channel = channel.id
    page = 1
    has_more = True
    api = slack.api.files
    slack.log.debug('list all files(user=%s, after=%s, before=%s, types=%s, channel=%s', user, after, before, types,
                    channel)

    while has_more:
      res = api.list(user=user, ts_from=after, ts_to=before, types=types, channel=channel, page=page, count=100).body

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

    :return:  None if successful else exception
    :rtype: Exception
    """
    try:
      # No response is a good response so no error
      self.api.delete(self.id)
      self._slack.log.deleted(self)
      return None
    except Exception as error:
      self._slack.log.deleted(self, error)
      return error

  def download_response(self, **kwargs):
    """
    downloads this file using python requests module

    :return: python requests Response object
    :rtype: Response
    """
    import requests
    headers = {
      'Authorization': 'Bearer ' + self._slack.token
    }
    return requests.get(self.json['url_private_download'], headers=headers, **kwargs)

  def download_json(self):
    """
    downloads this file and returns the JSON content

    :return: json content
    :rtype: dict,list
    """
    res = self.download_response()
    return res.json()

  def download_content(self):
    """
    downloads this file and returns the raw content

    :return: the content
    :rtype: bytes[]
    """
    res = self.download_response()
    return res.content

  def download_stream(self, chunk_size=1024):
    """
    downloads this file and returns a content stream

    :return: bytes[] chunk stream
    :rtype: *bytes[]
    """
    res = self.download_response(stream=True)
    return res.iter_content(chunk_size=chunk_size)

  def download_to(self, directory='.'):
    """
    downloads this file to the given directory

    :return: the stored file path
    :rtype: str
    """
    from os import path

    file_name = path.join(directory, self.name)
    return self.download(file_name)

  def download(self, file_name=None):
    """
    downloads this file to the given file name

    :return: the stored file name
    :rtype: str
    """
    with open(file_name or self.name, 'wb') as out:
      for chunk in self.download_stream():
        out.write(chunk)
    return file_name


def _parse_time(time_str):
  import time

  if time_str is None:
    return None
  if isinstance(time_str, (int, float)):
    return int(time_str)
  try:
    if len(time_str) == 8:
      return time.mktime(time.strptime(time_str, '%Y%m%d'))
    return time.mktime(time.strptime(time_str, '%Y%m%d%H%M'))
  except ValueError:
    return None


def _find_user(users, msg):
  if 'user' not in msg:
    return None
  userid = msg['user']
  return users.get(userid)
