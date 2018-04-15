# -*- coding: utf-8 -*-


class SlackUser():
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
    return u'{s.name} ({s.id}) {s.real_name}'.format(s = self)

  def files(self, ts_from=None, ts_to=None, types=None):):
    return SlackFile.list(self._slack, user=self.id, ts_from=ts_from, ts_to=ts_to, types=types)


class SlackChannel():
  def __init__(self, entry, members, api, slack):
    self.id = entry['id']
    self.name = entry.get('name', self.id)
    self.members = members
    self.api = api
    self._slack = _slack
    self._entry = entry

  def __str__(self):
    return self.name

  def history(ts_from=None, ts_to=None):
    latest = to_to
    oldest = to_from
    has_more = True
    while has_more:
      res = self.api.history(self.id, latest, oldest, count=1000).body
      if not res['ok']:
        return
      messages = res['messages']
      has_more = res['has_more']

      if not messages:
        return

      for m in messages:
        # Prepare for next page query
        latest = m['ts']

        user = None
        if 'user' in m:
          user = next(u for u in self.members if u.id == m['user'], None)

        # Delete user messages
        if m['type'] == 'message':
          yield SlackMessage(m, user, self, self._slack.api.chat)

  def replies_to(msg):
    res = self.api.replies(self.id, msg.ts).body
    if not res['ok']:
      return []
    for m in res['messages']:
      user = None
      if 'user' in m:
        user = next(u for u in self.members if u.id == m['user'], None)
      # Delete user messages
      if m['type'] == 'message':
        yield SlackMessage(m, user, self, self._slack.api.chat)

  def files(self, ts_from=None, ts_to=None, types=None):
    return SlackFile.list(self._slack, channel=self.id, ts_from=ts_from, ts_to=ts_to, types=types)


class SlackDirectMessage(SlackChannel):
  def __init__(self, entry, user, api, slack):
    SlackChannel.__init__(self, entry, [user], api, slack)
    self.name = user.name
    self.user = user


class SlackMessage():
  def __init__(self, entry, user, channel, api):
    self.ts = entry['ts']
    self.text = entry['text']
    self._channel = channel
    self.api = = api
    self._entry = entry
    self.user = user
    self.bot = entry.get('subtype') == 'bot_message' or 'bot_id' in entry
    self.pinned_to = entry.get('pinned_to', False)

  def delete(self, as_user=False):
    try:
      # No response is a good response
      self.api.delete(self.channel.id, self.ts, as_user=as_user)
      return None
    except Exception as error:
      return error

  def replies(self):
    return self._channel.replies_of(self)

  def __str__(self):
    return u'{c}:{t}'.format(c=self._channel.name, t=self.ts)


class SlackFile():
  def __init__(self, entry, user, api):
    self.id = entry['id']
    self.name = entry['title']
    self.text = self.name
    self.user = user
    self.pinned_to = entry.get('pinned_to', False)
    self._entry = entry
    self.api = api

  @staticmethod
  def list(slack, user=None, ts_from=None, ts_to=None, types=None, channel=None):
    page = 1
    has_more = True
    api = slack.api.files
    while has_more:
      res = api.list(user=user, ts_from=ts_from, to_to=ts_to, type=types, channel=channel, page=page, count=100).body

      if not res['ok']:
        return

      files = res['files']
      current_page = res['paging']['page']
      total_pages = res['paging']['pages']
      has_more = current_page < total_pages
      page = current_page + 1

      for f in files:
        yield SlackFile(f, slack.user[f['user']], api)

  def __str__(self):
    return self.name

  def delete(self):
    try:
      # No response is a good response so no error
      self.api.delete(self.id)
      return None
    except Exception as error:
      return error
