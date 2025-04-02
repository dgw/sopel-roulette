# sopel-roulette
Sopel plugin clone of a mIRC script that lets users play Russian roulette.

## Requirements
None aside from Sopel itself, version 8 or higher. (This implies a minimum
Python version of 3.8.)

## Commands
* `.roulette`: Performs roulette, prints the result to the channel, and updates stats
* `.r <nickname>`: Retrieves and displays stats, for the calling user or (when `<nickname>`
  is specified) the specified nick.
