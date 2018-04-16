# -*- coding: utf-8 -*-


def get_mpdirect_ids_by_pattern(pattern):
  res = slack.mpim.list().body
  if not res['ok'] or not res['groups']:
    return []
  mpims = res['groups']

  regex = re.compile('^' + pattern + '$', re.I)

  def matches(members):
    names = [user_dict[m] for m in mpim['members']]
    # has to match at least one permutation of the members
    for permutation in itertools.permutations(names):
      if (regex.match(','.join(permutation))):
        return True
    return False

  return [(mpim['id'], ','.join(user_dict[m] for m in mpim['members'])) for mpim in mpims if matches(mpim['members'])]
