__author__ = 'Lin, Ke-fei, Samuel Gratzl'
__authoremail__ = 'kfei@kfei.net, samuel_gratzl@gmx.at'
__version__ = '1.0.0'

from .cleaner import SlackCleaner
from .predicates import is_not_pinned, is_bot, match, name, match_text, match_user, is_member, by_user, by_users
