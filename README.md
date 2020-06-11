# wiihacky

An experimental bot for subreddit and discord moderation

Current Stage: Fleshing Out Functionality, DB Integration, Reddit Integration.

## Requirements

1. discord bot token to login to discord.
2. a mysql database with login information to log into a db.
3. A redis database for the user system.
4. a bot setup for reddit if you want to use the main portion of the bot
5. a python 3.7+ install with the libs specified in the requirements.txt

## Instructions

1. Get this repo onto the place you want to run it from.
2. Set your discord token in your environment variables:
`DISCORD_BOT_TOKEN=put_your_token_here`
3. Run the main script: `python3 ./wiihacky`
Though it would most likely be better to create a data
directory and run it from there...
```
mkdir datadir;cd datadir
python3 ../wiihacky
```
ie; make sure you're in a directory you won't mind the bot writing stuff in
. All logon credentials and tokens are obtained from env variables.

Extra: You can also put in DB creds for a mysql db, redis info, as well as
reddit bot credentials all in env so the bot will connect to those platforms
. Information on how to do this is in the Memory, and Reddit cog docstrings.

We're licensed under MIT, and would also like to give credit to the Python
 Discord Bot : https://github.com/python-discord/bot
 
 Where some of the code for this bot was both inspired by and copied from.
