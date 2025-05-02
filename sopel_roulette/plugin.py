"""sopel-roulette

Sopel plugin clone of a mIRC script to let users play Russian roulette

Copyright (c) 2015-2025 dgw

Licensed under the Eiffel Forum License 2
"""
from __future__ import annotations

import math
import random
import time
from typing import TYPE_CHECKING

from sopel import plugin, tools
from sopel.config import types


if TYPE_CHECKING:
    from sopel.bot import Sopel
    from sopel.config import Config
    from sopel.trigger import Trigger


class RouletteSection(types.StaticSection):
    mode = types.ChoiceAttribute(
        'mode',
        ['random', 'revolver'],
        default='random',
    )
    """The game mode.

    - `random`: winning is based solely on a random number generator.
    - `revolver`: the bullet is loaded into a random chamber and the revolver
      advances one slot after each trigger pull.
    """

    chambers = types.ValidatedAttribute(
        'chambers',
        int,
        str,
        default=6,
    )
    """How many chambers the revolver has — 6 by default.

    The chance of losing is the reciprocal of this number.
    """

    timeout = types.ValidatedAttribute('timeout', int, default=600)
    """The timeout (in seconds) between games of roulette by the same user."""


def configure(config: Config) -> None:
    config.define_section('roulette', RouletteSection)
    config.roulette.configure_setting(
        'mode',
        'Game mode ({}):'.format(', '.join(RouletteSection.mode.choices)),
    )
    config.roulette.configure_setting(
        'chambers',
        'Number of chambers in the revolver (default: 6):',
    )
    config.roulette.configure_setting(
        'timeout',
        'Timeout between roulette trigger pulls by the same user (in seconds):',
    )


def setup(bot: Sopel) -> None:
    bot.settings.define_section('roulette', RouletteSection)


def play_revolver(bot: Sopel, trigger: Trigger) -> bool:
    """Play a round of Russian roulette with a revolver.

    Each channel has a revolver with 6 chambers, and the bullet is loaded into
    one at random. The revolver advances one slot after each trigger pull.
    """
    channel = trigger.sender
    chamber = bot.db.get_channel_value(
        channel,
        'roulette_bullet_pos',
        random.randint(1, bot.settings.roulette.chambers),
    )

    chamber -= 1
    if chamber <= 1:
        bot.db.delete_channel_value(channel, 'roulette_bullet_pos')
        won = False
    else:
        bot.db.set_channel_value(channel, 'roulette_bullet_pos', chamber)
        won = True

    return won


@plugin.command('roulette')
@plugin.require_chanmsg
def roulette(bot: Sopel, trigger: Trigger) -> None | int:
    settings = bot.settings.roulette
    time_since = time_since_roulette(bot, trigger.nick)
    if time_since < settings.timeout:
        bot.notice(
            "Next roulette attempt will be available {}.".format(
                tools.time.seconds_to_human(
                    -(settings.timeout - time_since)
                )
            ),
            trigger.nick,
        )
        return plugin.NOLIMIT

    if settings.mode == 'random':
        won = random.randint(1, settings.chambers) == 1
    elif settings.mode == 'revolver':
        won = play_revolver(bot, trigger)
    else:
        bot.reply("Unknown roulette mode '%s'." % settings.mode)
        return plugin.NOLIMIT

    if won:
        bot.say("Click! %s is lucky; there was no bullet." % trigger.nick)
    else:
        bot.say("BANG! %s is dead!" % trigger.nick)

    bot.db.set_nick_value(trigger.nick, 'roulette_last', time.time())
    update_roulettes(bot, trigger.nick, won)


@plugin.commands('roulettes', 'r')
def roulettes(bot: Sopel, trigger: Trigger) -> None | int:
    target = trigger.group(3) or trigger.nick
    games, wins = get_roulettes(bot, target)
    if not games:
        bot.say("%s hasn't played Russian roulette yet." % target)
        return
    g_times = 'time' if games == 1 else 'times'
    bot.say(
        "%s has survived Russian roulette %d out of %d %s (or %.2f%%)."
        % (target, wins, games, g_times, wins / games * 100)
    )


def update_roulettes(bot: Sopel, nick: str, won: bool = False) -> None:
    """Update the number of roulette games played and won by the user."""
    games, wins = get_roulettes(bot, nick)
    games += 1
    if won:
        wins += 1
    bot.db.set_nick_value(nick, 'roulette_games', games)
    bot.db.set_nick_value(nick, 'roulette_wins', wins)


def get_roulettes(bot: Sopel, nick: str) -> tuple[int, int]:
    """Return the number of roulette games played and won by the user."""
    games = bot.db.get_nick_value(nick, 'roulette_games') or 0
    wins = bot.db.get_nick_value(nick, 'roulette_wins') or 0
    return games, wins


def time_since_roulette(bot: Sopel, nick: str) -> int:
    """Return the time in seconds since the user's last roulette game."""
    now = time.time()
    last = bot.db.get_nick_value(nick, 'roulette_last') or 0
    return math.ceil(abs(now - last))
