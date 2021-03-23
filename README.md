# Care and Feeding

## The **I Know Nothing** bot

This Discord bot is intended to fill in a few gaps of the Electric Eye
(Urban Dead) bot. The initial function is to print a list of active
players of the The Know Nothings (TKN) group.

## Setup

On my systems, I had to install the following python3 modules:

- discord.py
- python-dotenv
- lxml

The basic bot configuration is done by way of an .env file,
please refer to .env.sample

The bot also requires the use of a (dedicated) Urban Dead alt/character
to print the list of the group's currently active (non-MIA) players.
The **active**, **mia**, and **group** commands will query the alts using
the default coloring (grey). Other colors are reserved for future use,
like supporting multiple groups for a single alt.

For Debian/Ubuntu hosts, see iknbot.service.sample for a sample
systemd service file.

## Commands

Not much to see at this point:

*   %help

    What it says on the tin, print the bot's help text.

*   ping

    The "Hello World" equivalent. Should be removed/made hidden.

*   active

    Return the list of active (non-MIA) players on the contact list.

*   mia

    Return the list of non-active (MIA) players on the contact list.

*   group

    Return an overview of the group's active/MIA status

