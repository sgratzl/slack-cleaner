__author__ = 'Samuel Gratzl, Lin, Ke-fei'
__authoremail__ = 'samuel_gratzl@gmx.at, kfei@kfei.net'
__version__ = '1.0.0'

from .cleaner import SlackCleaner
from .predicates import is_not_pinned, is_bot, match, name, match_text, match_user, is_member, by_user, by_users
