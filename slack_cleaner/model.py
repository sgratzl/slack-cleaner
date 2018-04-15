
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
  def __init__(self, entry, members, api):
    self.id = entry['id']
    self.name = entry['name']
    self.members = members
    self.api = api
    self._entry = entry

  def __str__(self):
    return self.name


class SlackDirectMessage():
  def __init__(self, entry, user, api):
    self.id = entry['id']
    self.name = user.name
    self.user = user
    self.members = [user]
    self._entry = entry

  def __str__(self):
    return str(self.user)
