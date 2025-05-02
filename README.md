# sopel-roulette

Sopel plugin clone of a mIRC script to let users play Russian roulette

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-roulette
```

### Requirements

None aside from Sopel itself, version 8 or higher. (This implies a minimum
Python version of 3.8.)

## Configuring

The easiest way to configure `sopel-roulette` is via Sopel's configuration
wizard—simply run `sopel-plugins configure roulette` and enter the values for
which it prompts you.

### Available options

This plugin's default settings ("random" `mode` with 6 `chambers` and a
600-second `timeout`) mimic the source mIRC script, but the values are
customizable as described here:

* `chambers`: 6 by default\
  How many chambers the revolver cylinder has. The chance of losing is
  `1/chambers`.
* `mode`: `random` (the default) or `revolver`
  * In `random` mode, winning is a simple dice roll, `1 == randint(1, chambers)`.
  * In `revolver` mode, the game places the bullet in a specific chamber (per
  channel) and advances it each time someone plays.
* `timeout`: 600 by default\
  Cooldown in seconds between games, for each user.

## Using

* `.roulette`: Performs a game of Russian roulette, prints the result to the
  channel, and updates the user's stats
* `.r [nickname]`: Retrieves and displays stats for the calling user, or (when
  `nickname` is specified) the specified nick.
