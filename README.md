# wiihacky

An experimental bot for subreddit and discord moderation

Current Stage: Fleshing Out Functionality, DB Integration, Reddit Integration.

## Requirements

1. discord bot token to login to discord.
2. a mysql database with login information to log into a db.
Currently mysql is all wiihacky supports.
3. a bot setup for reddit if you want to use the main portion
of the bot
4. a python 3.7+ install with the following libs and their 
reqs:

    * discord.py
    * discord_interactive
    * praw
    * PyYaml
    * SQLAlchemy
    * aiofiles, aiofiles-ext
    * aiohttp (required by discord.py)
    * aiomysql
    


## Instructions

1. Get this repo onto the place you want to run it from.
2. Set your discord token in your environment variables:
`DISCORD_BOT_TOKEN=put_your_token_here`
3. Run the main script: `python3 ./wiihacky`
Though it would most likely be better to create a data
directory and run it from there...
    ```
    mkdir datadir;cd datadir
    python3 ../wiihacky.py
    ```
    ie; make sure you're in a directory you won't mind the bot
writing stuff in. All logon credentials and tokens are
obtained from env variables.

[![Run on Repl.it](https://repl.it/badge/github/bloodythorn/wiihacky)](https://repl.it/github/bloodythorn/wiihacky)