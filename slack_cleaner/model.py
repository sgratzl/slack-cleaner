import time


class SlackUser():
  def __init__(self, member):
    self.id = member['id']
    self.name = member['name']
    self.real_name = member['profile'].get('real_name')
    self.display_name = member['profile']['display_name']
    self.email = member['profile'].get('email')
    self._entry = member
    self.is_bot = member['is_bot']
    self.is_app_user = member['is_app_user']
    self.bot = self.is_bot or self.is_app_user

  def __str__(self):
    return '{s.name} ({s.id}) {s.real_name}'.format(s = self)


class SlackChannel():
  def __init__(self, entry, members, api, chat_api):
    self.id = entry['id']
    self.name = entry.get('name', self.id)
    self.members = members
    self.api = api
    self._chat_api = chat_api
    self._entry = entry

  def __str__(self):
    return self.name


  def history(oldest = None, latest = None):
    has_more = True
    while has_more:
      res = self.api.history(self.id, latest, oldest).body
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
          yield SlackMessage(m, user, self, self._chat_api)


class SlackMessage():
  def __init__(self, entry, user, channel, api):
    self.ts = entry['ts']
    self._channel = channel
    self.api = = api
    self._entry = entry
    self.user = user
    self.bot = entry.get('subtype') == 'bot_message' or 'bot_id' in entry


  def delete(as_user=False):
    self.api.delete(self.channel.id, self.ts, as_user=as_user)


class SlackDirectMessage(SlackChannel):
  def __init__(self, entry, user, api, chat_api):
    SlackChannel.__init__(self, entry, [user], api, chat_api)
    self.name = user.name
    self.user = user


class SlackFile():
  def __init__(self, entry, api):
    self.id = entry['id']
    self.name = entry['title']
    self._entry = entry
    self.api = api

  def delete():
    try:
      # No response is a good response
      self.api.delete(self.id)
      return True
    except Exception as error:
      # TODO
      return False
