"""sopel-chanlogs

A channel logging plugin for Sopel IRC bots

Built on an original plugin by David Baumgold <david@davidbaumgold.com>, 2014
Continued by Elsie Powell, Max Gurela, dgw, and other contributors

Licensed under the Eiffel Forum License 2

https://sopel.chat/
"""
from __future__ import annotations

from datetime import datetime
import os.path
import re
import threading

import pytz

from sopel import plugin
from sopel.config.types import (
    BooleanAttribute,
    FilenameAttribute,
    StaticSection,
    ValidatedAttribute,
)
from sopel.tools.memories import SopelMemoryWithDefault


MESSAGE_TPL = "{datetime}  <{trigger.nick}> {message}"
ACTION_TPL = "{datetime}  * {trigger.nick} {message}"
NICK_TPL = "{datetime}  *** {trigger.nick} is now known as {trigger.sender}"
JOIN_TPL = "{datetime}  *** {trigger.nick} has joined {trigger}"
PART_TPL = "{datetime}  *** {trigger.nick} has left {trigger}"
QUIT_TPL = "{datetime}  *** {trigger.nick} has quit IRC"
TOPIC_TPL = "{datetime}  *** {trigger.nick} changed the topic to {trigger.args[1]}"
# According to Wikipedia
BAD_CHARS = re.compile(r'[\/?%*:|"<>. ]')


class ChanlogsSection(StaticSection):
    dir = FilenameAttribute('dir', directory=True, default='~/chanlogs')
    """Path to channel log storage directory"""
    by_day = BooleanAttribute('by_day', default=True)
    """Split log files by day"""
    privmsg = BooleanAttribute('privmsg', default=False)
    """Record private messages"""
    microseconds = BooleanAttribute('microseconds', default=False)
    """Microsecond precision"""
    localtime = BooleanAttribute('localtime', default=False)
    """Attempt to use preferred timezone instead of UTC"""
    # TODO: Allow configuration of templates; perhaps the user would like to use
    #       parsers that support only specific formats.
    message_template = ValidatedAttribute('message_template', default=None)
    action_template = ValidatedAttribute('action_template', default=None)
    join_template = ValidatedAttribute('join_template', default=None)
    part_template = ValidatedAttribute('part_template', default=None)
    quit_template = ValidatedAttribute('quit_template', default=None)
    nick_template = ValidatedAttribute('nick_template', default=None)
    topic_template = ValidatedAttribute('topic_template', default=None)


def configure(config):
    config.define_section('chanlogs', ChanlogsSection, validate=False)
    config.chanlogs.configure_setting(
        'dir',
        'Path to channel log storage directory',
    )


def get_datetime(bot):
    """Get a datetime object of the current time."""
    dt = datetime.now(pytz.utc)
    target_tz = bot.config.core.default_timezone

    if bot.config.chanlogs.localtime and target_tz != 'UTC':
        # small optimization above, making sure not to convert UTC to UTC
        target_tz = pytz.timezone(target_tz)
        dt = dt.astimezone(target_tz)

    if not bot.config.chanlogs.microseconds:
        dt = dt.replace(microsecond=0)

    return dt


def get_fpath(bot, trigger, channel=None):
    """Get the appropriate log file path.

    Returns a string corresponding to the path to the file where the message
    currently being handled should be logged.
    """
    basedir = bot.config.chanlogs.dir
    channel = channel or trigger.sender
    channel = channel.lstrip("#")
    channel = BAD_CHARS.sub('__', channel)
    channel = bot.make_identifier(channel).lower()

    dt = get_datetime(bot)
    if bot.config.chanlogs.by_day:
        fname = "{channel}-{date}.log".format(channel=channel, date=dt.date().isoformat())
    else:
        fname = "{channel}.log".format(channel=channel)
    return os.path.join(basedir, fname)


def _format_template(tpl, bot, trigger, **kwargs):
    dt = get_datetime(bot)

    formatted = tpl.format(
        trigger=trigger, datetime=dt.isoformat(),
        date=dt.date().isoformat(), time=dt.time().isoformat(),
        **kwargs
    ) + "\n"

    return formatted


def setup(bot):
    bot.config.define_section('chanlogs', ChanlogsSection)

    # locks for log files
    if 'chanlog_locks' not in bot.memory:
        bot.memory['chanlog_locks'] = SopelMemoryWithDefault(threading.Lock)


@plugin.rule('.*')
@plugin.echo
@plugin.unblockable
def log_message(bot, message):
    """Log all messages, including Sopel's own"""
    # if this is a private message and we're not logging those, return early
    if message.sender.is_nick() and not bot.config.chanlogs.privmsg:
        return

    # determine which template we want, message or action
    if message.startswith("\001ACTION ") and message.endswith("\001"):
        tpl = bot.config.chanlogs.action_template or ACTION_TPL
        # strip off start and end
        message = message[8:-1]
    else:
        tpl = bot.config.chanlogs.message_template or MESSAGE_TPL

    logline = _format_template(tpl, bot, message, message=message)
    fpath = get_fpath(bot, message)
    with bot.memory['chanlog_locks'][fpath]:
        with open(fpath, "ab") as f:
            f.write(logline.encode('utf8'))


@plugin.rule('.*')
@plugin.event("JOIN")
@plugin.unblockable
def log_join(bot, trigger):
    """Log joins"""
    tpl = bot.config.chanlogs.join_template or JOIN_TPL
    logline = _format_template(tpl, bot, trigger)
    fpath = get_fpath(bot, trigger, channel=trigger.sender)
    with bot.memory['chanlog_locks'][fpath]:
        with open(fpath, "ab") as f:
            f.write(logline.encode('utf8'))


@plugin.rule('.*')
@plugin.event("PART")
@plugin.unblockable
def log_part(bot, trigger):
    """Log parts"""
    tpl = bot.config.chanlogs.part_template or PART_TPL
    logline = _format_template(tpl, bot, trigger=trigger)
    fpath = get_fpath(bot, trigger, channel=trigger.sender)
    with bot.memory['chanlog_locks'][fpath]:
        with open(fpath, "ab") as f:
            f.write(logline.encode('utf8'))


@plugin.rule('.*')
@plugin.event("QUIT")
@plugin.unblockable
@plugin.thread(False)
@plugin.priority('high')
def log_quit(bot, trigger):
    """Log quits"""
    tpl = bot.config.chanlogs.quit_template or QUIT_TPL
    logline = _format_template(tpl, bot, trigger)
    # make a copy of Sopel's channel list that we can safely iterate over
    channels_copy = list(bot.channels.values())
    # write logline to *all* channels that the user was present in
    for channel in channels_copy:
        if trigger.nick in channel.users:
            fpath = get_fpath(bot, trigger, channel.name)
            with bot.memory['chanlog_locks'][fpath]:
                with open(fpath, "ab") as f:
                    f.write(logline.encode('utf8'))


@plugin.rule('.*')
@plugin.event("NICK")
@plugin.unblockable
def log_nick_change(bot, trigger):
    """Log nick changes"""
    tpl = bot.config.chanlogs.nick_template or NICK_TPL
    logline = _format_template(tpl, bot, trigger)
    old_nick = trigger.nick
    new_nick = trigger.sender
    # make a copy of Sopel's channel list that we can safely iterate over
    channels_copy = list(bot.channels.values())
    # write logline to *all* channels that the user is present in
    for channel in channels_copy:
        if old_nick in channel.users or new_nick in channel.users:
            fpath = get_fpath(bot, trigger, channel.name)
            with bot.memory['chanlog_locks'][fpath]:
                with open(fpath, "ab") as f:
                    f.write(logline.encode('utf8'))


@plugin.rule('.*')
@plugin.event("TOPIC")
@plugin.unblockable
def log_topic(bot, trigger):
    """Log topic changes"""
    tpl = bot.config.chanlogs.topic_template or TOPIC_TPL
    logline = _format_template(tpl, bot, trigger)
    fpath = get_fpath(bot, trigger, channel=trigger.sender)
    with bot.memory['chanlog_locks'][fpath]:
        with open(fpath, "ab") as f:
            f.write(logline.encode('utf8'))
