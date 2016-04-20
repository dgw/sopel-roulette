# sopel-roulette
Clone of a mIRC script that lets users play Russian roulette.

## Requirements
Aside from sopel itself, depends on the standard Python libraries `random` and `time`.

Also imports Python 3-style division from `__future__`, so version of Python with support
for this is needed.

## Commands
* `.roulette`: Performs roulette, prints the result to the channel, and updates stats
* `.r <nickname>`: Retrieves and displays stats, for the calling user or (when `<nickname>`
  is specified) the specified nick.

