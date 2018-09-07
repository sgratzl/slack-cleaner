# -*- coding: utf-8 -*-
"""slack_cleaner2 is a simple api for deleting slack messages"""

from ._info import __version__, __author__, __email__, __license__
from .predicates import and_, or_, is_not_pinned, is_bot, match, is_name, match_text, match_user, is_member, by_user, \
  by_users
from .slack_cleaner2 import SlackCleaner
from .util import a_while_ago

__all__ = ['__version__', '__author__', '__email__', '__license__', 'SlackCleaner', 'and_', 'or_', 'is_not_pinned', 'is_bot', 'match', 'is_name', 'match_text', 'match_user',
           'is_member', 'by_user', 'by_users', 'a_while_ago']
