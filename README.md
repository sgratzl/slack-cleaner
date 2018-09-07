# slack_cleaner2

[![License: MIT][mit-image]][mit-url] [![CircleCI][ci-image]][ci-url] [![PyPi][pypi-image]][pypi-url] [![Read the Docs][docs-image]][docs-url]

Bulk delete messages and files on Slack.

## Install

Install from PyPi:

```bash
pip install slack_cleaner2
```

latest version
```bash
pip install -e git+https://github.com/sgratzl/slack_cleaner.git@develop
```

## Usage

In contrast to the original version (https://github.com/kfei/slack-cleaner) this version is a focusing on pure python package that allows for easy scripting instead of a vast amount of different command line arguments. 

basic usage

```python
from slack_cleaner2 import *

s = SlackCleaner('SECRET TOKEN')
# list of users
s.users
# list of all kind of channels
s.conversations

# delete all messages in -bozs channels
for msg in s.msgs(filter(match('.*-bots'), s.conversations)):
  msg.delete()
```


## Tokens

You will need to generate a Slack legacy token to use slack-cleaner. You can generate a token [here](https://api.slack.com/custom-integrations/legacy-tokens):

[https://api.slack.com/custom-integrations/legacy-tokens](https://api.slack.com/custom-integrations/legacy-tokens)



## Minimal Slack permission scopes required

- `channels:history`
- `channels:read`
- `chat:write:bot`
- `users:read`


## Credits

**To all the people who can only afford a free plan. :cry:**

[mit-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[mit-url]: https://opensource.org/licenses/MIT
[ci-image]: https://circleci.com/gh/sgratzl/slack_cleaner/tree/develop.svg?style=shield
[ci-url]: https://circleci.com/gh/sgratzl/slack_cleaner/tree/develop
[pypi-image]: https://pypip.in/version/slack_cleaner2/badge.svg
[pypi-url]: https://pypi.python.org/pypi/slack_cleaner2/
[docs-image]: https://readthedocs.org/projects/slack-cleaner2/badge/?version=latest
[docs-url]: https://slack-cleaner2.readthedocs.io/en/latest/?badge=latest
