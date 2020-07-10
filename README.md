# slack-cleaner
[![License: MIT][mit-image]][mit-url] [![PyPi][pypi-image]][pypi-url]

Bulk delete messages and files on Slack.

this is a fork of https://github.com/kfei/slack-cleaner

An improved Python module based version is located at https://github.com/sgratzl/slack_cleaner2

## Install

Install from Pip:

```bash
pip install slack-cleaner
```

current development version:

```
pip install -e git+https://github.com/sgratzl/slack-cleaner.git#egg=slack-cleaner
```

If you prefer Docker, there is a pre-built Docker image as well:

```bash
docker pull sgratzl/slack-cleaner
```

Just use `docker run -it --rm sgratzl/slack-cleaner -c "slack-cleaner ..."` for each command or jump into a shell using `docker run -it --rm sgratzl/slack-cleaner`.

Install for Fedora or EPEL7

[@rapgro](https://github.com/rapgro) maintains packages for both Fedora and EPEL7

```bash
# Fedora
dnf install slack-cleaner
# EPEL7
yum install -y epel-release ; yum install slack-cleaner
```

## Arguments

```
usage: slack-cleaner [-h] --token TOKEN [--log] [--quiet] [--rate RATE]
                     [--as_user] [--message | --file | --info] [--regex]
                     [--channel CHANNEL] [--direct DIRECT] [--group GROUP]
                     [--mpdirect MPDIRECT] [--user USER] [--botname BOTNAME]
                     [--bot] [--keeppinned] [--after AFTER] [--before BEFORE]
                     [--types TYPES] [--pattern PATTERN] [--perform]

optional arguments:
  -h, --help           show this help message and exit
  --token TOKEN        Slack API token (https://api.slack.com/web) or SLACK_TOKEN env var
  --log                Create a log file in the current directory
  --quiet              Run quietly, does not log messages deleted
  --proxy              Proxy Server url:port
  --verify             Verify option for Session (http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification)
  --rate RATE          Delay between API calls (in seconds)
  --as_user            Pass true to delete the message as the authed user. Bot
                       users in this context are considered authed users.
  --message            Delete messages
  --file               Delete files
  --info               Show information
  --regex              Interpret channel, direct, group, and mpdirect as regex
  --channel CHANNEL    Channel name's, e.g., general
  --direct DIRECT      Direct message's name, e.g., sherry
  --group GROUP        Private group's name
  --mpdirect MPDIRECT  Multiparty direct message's name, e.g.,
                       sherry,james,johndoe
  --user USER          Delete messages/files from certain user
  --botname BOTNAME    Delete messages/files from certain bots. Implies '--bot'
  --bot                Delete messages from bots
  --keeppinned         exclude pinned messages from deletion
  --after AFTER        Delete messages/files newer than this time (YYYYMMDD)
  --before BEFORE      Delete messages/files older than this time (YYYYMMDD)
  --types TYPES        Delete files of a certain type, e.g., posts,pdfs
  --pattern PATTERN    Delete messages/files with specified pattern or if one of their attachments matches (regex)
  --perform            Perform the task
```

## Permission Scopes needed

The permissions to grant depend on what you are going to use the script for.
Grant the permissions below depending on your use.

Beyond granting permissions, if you wish to use this script to delete
messages or files posted by others, you will need to be an [Owner or
Admin](https://get.slack.help/hc/en-us/articles/218124397-Change-a-member-s-role)
of the workspace.

#### Deleting messages from public channels

- `channels:history`
- `channels:read`
- `chat:write` (or both `chat:write:user` and `chat:write:bot` for older apps)
- `users:read`

#### Deleting messages from private channels

- `groups:history`
- `groups:read`
- `chat:write` (or `chat:write:user` for older apps)
- `users:read`

#### Deleting messages from 1:1 IMs

- `im:history`
- `im:read`
- `chat:write` (or `chat:write:user` for older apps)
- `users:read`

#### Deleting messages from multi-person IMs

- `mpim:history`
- `mpim:read`
- `chat:write` (or `chat:write:user` for older apps)
- `users:read`

#### Deleting files

- `files:read`
- `files:write` (or `files:write:user` for older apps)
- `users:read`

## Usage

```bash
# Delete all messages from a channel
slack-cleaner --token <TOKEN> --message --channel general --user "*"

# Delete all messages from a private group aka private channel
slack-cleaner --token <TOKEN> --message --group hr --user "*"

# Delete all messages from a direct message channel
slack-cleaner --token <TOKEN> --message --direct sherry --user johndoe

# Delete all messages from a multiparty direct message channel. Note that the
# list of usernames must contains yourself
slack-cleaner --token <TOKEN> --message --mpdirect sherry,james,johndoe --user "*"

# Delete all messages from certain user
slack-cleaner --token <TOKEN> --message --channel gossip --user johndoe

# Delete all messages from bots (especially flooding CI updates)
slack-cleaner --token <TOKEN> --message --channel auto-build --bot

# Delete all messages older than 2015/09/19
slack-cleaner --token <TOKEN> --message --channel general --user "*" --before 20150919

# Delete all files
slack-cleaner --token <TOKEN> --file --user "*"

# Delete all files from certain user
slack-cleaner --token <TOKEN> --file --user johndoe

# Delete all snippets and images
slack-cleaner --token <TOKEN> --file --types snippets,images

# Show information about users, channels:
slack-cleaner --token <TOKEN> --info

# Delete matching a regexp pattern
slack-cleaner --token <TOKEN> --pattern "(bar|foo.+)"

# TODO add add keep_pinned example, add quiet

# Always have a look at help message
slack-cleaner --help
```

## Configuring app

The cleaner needs you to give Slack's API permission to let it run the
operations it needs. You grant these by registering it as an app in the
workspace you want to use it in.

You can grant these permissions to the app by:

1. going to [Your Apps](https://api.slack.com/apps)
2. select 'Create New App', fill out an App Name (eg 'Slack Cleaner') and
   select the Slack workspace you want to use it in
3. select 'OAuth & Permissions' in the sidebar
4. scroll down to Scopes and select all scopes you need
5. select 'Save changes'
6. select 'Install App to Workspace'
7. review the permissions and press 'Authorize'
8. copy the 'OAuth Access Token' shown, and use this token as the `--token`
   argument to the script

## Tips

After the task, a backup file `slack-cleaner.<timestamp>.log` will be created in current directory if `--log` is supplied.

If any API problem occurred, try `--rate=<delay-in-seconds>` to reduce the API call rate (which by default is unlimited).

If you see the following warning from `urllib3`, consider to install missing
packages: `pip install --upgrade requests[security]` or just upgrade your Python to 2.7.9.

```
InsecurePlatformWarning: A true SSLContext object is not available.
          This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail.
          For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
```

## Credits

**To all the people who can only afford a free plan. :cry:**


[mit-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[mit-url]: https://opensource.org/licenses/MIT
[pypi-image]: https://pypip.in/version/slack-cleaner/badge.svg
[pypi-url]: https://pypi.python.org/pypi/slack-cleaner/
