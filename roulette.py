"""sopel-roulette

Sopel plugin clone of a mIRC script to let users play Russian roulette

Copyright (c) 2015-2025 dgw

Licensed under the Eiffel Forum License 2.0
"""

from __future__ import annotations

from datetime import datetime
import math
import random

from sopel import plugin, tools
from sopel.config.types import StaticSection, ValidatedAttribute


class RouletteSection(StaticSection):
    timeout = ValidatedAttribute('timeout', int, default=600)
    """The timeout (in seconds) between roulette trigger pulls by the same user."""


def configure(config):
    config.define_section('roulette', RouletteSection)
    config.roulette.configure_setting(
        'timeout',
        'Timeout between roulette trigger pulls by the same user (in seconds): ',
    )


def setup(bot):
    bot.config.define_section('roulette', RouletteSection)


@plugin.command('roulette')
@plugin.require_chanmsg
def roulette(bot, trigger):
    time_since = time_since_roulette(bot.db, trigger.nick, trigger.time)
    if time_since < bot.config.roulette.timeout:
        bot.notice(
            "Next roulette attempt will be available {}.".format(
                tools.time.seconds_to_human(
                    -(bot.config.roulette.timeout - time_since)
                )
            ),
            trigger.nick,
        )
        return plugin.NOLIMIT
    if 6 != random.randint(1, 6):
        won = True
        bot.say("Click! %s is lucky; there was no bullet." % trigger.nick)
    else:
        won = False
        bot.say("BANG! %s is dead!" % trigger.nick)
    bot.db.set_nick_value(trigger.nick, 'roulette_last', trigger.time.timestamp())
    update_roulettes(bot.db, trigger.nick, won)


@plugin.commands('roulettes', 'r')
def roulettes(bot, trigger):
    target = trigger.group(3) or trigger.nick
    games, wins = get_roulettes(bot.db, target)
    if not games:
        bot.say("%s hasn't played Russian roulette yet." % target)
        return
    g_times = 'time' if games == 1 else 'times'
    bot.say(
        "%s has survived Russian roulette %d out of %d %s (or %.2f%%)."
        % (target, wins, games, g_times, wins / games * 100)
    )


def update_roulettes(db, nick, won=False):
    games, wins = get_roulettes(db, nick)
    games += 1
    if won:
        wins += 1
    db.set_nick_value(nick, 'roulette_games', games)
    db.set_nick_value(nick, 'roulette_wins', wins)


def get_roulettes(db, nick):
    games = db.get_nick_value(nick, 'roulette_games') or 0
    wins = db.get_nick_value(nick, 'roulette_wins') or 0
    return games, wins


def time_since_roulette(db, nick: str, now: datetime | float):
    if isinstance(now, datetime):
        now = now.timestamp()
    last = db.get_nick_value(nick, 'roulette_last') or 0
    return math.ceil(abs(now.timestamp() - last))
