# WiCS-Communication-Bot

This is a Discord bot built for the purpose of the WiCS olympics.
It has been made to facilitate score counting of the WiCS online events.

## Features

- when someone sends a messahge in #general, the bot triggers an event and contacts the person prompting them for their name, student email and student id.
- this bot will make use of the / commands, and modal UX from discord.
- this bot is useing a sheetDB API from https://sheetdb.io
- the bot will then enter this information into a google sheet and keep track of their scores related to this specific event.

## Installation

- Clone this repository
- Install the required packages: `pip install -r requirements.txt`
- Create a Discord bot account and get a token: https://discord.com/developers/docs/intro
- Data is being loaded into the following google sheets https://docs.google.com/spreadsheets/d/1_tbjYKJV16tLgdSZhFvqPNXarOEvg0nk9UIsmNx69qk/edit?gid=0#gid=0 
- Create a .env file in the root directory and add the following variables:

```
DISCORD_TOKEN=<your discord bot token>
```

- Run the bot: `python DiscordBot.py`
