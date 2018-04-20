# -*- coding: utf-8 -*-

"""slack_cleaner2 is a simple api for deleting slack messages"""

__author__ = """Samuel Gratzl"""
__email__ = 'samuel-gratzl@gmx.at'
__version__ = '0.1.0'

from .slack_cleaner2 import SlackCleaner
from .predicates import and_, or_, is_not_pinned, is_bot, match, is_name, match_text, match_user, is_member, by_user, by_users
from .util import a_while_ago

__all__ = ['SlackCleaner', 'and_', 'or_', 'is_not_pinned', 'is_bot', 'match', 'is_name', 'match_text', 'match_user', 'is_member', 'by_user', 'by_users', 'a_while_ago']
