# wiihacky

An experimental bot for subreddit and discord moderation. Currently also used for my experimentation in game development and language analysis.

## Current Stage: 

  1. Fleshing out functionality
  2. Adding moderator-related routines to aid in sub management
  3. Currently working on an ANN to analyze comments for possible rule violation.
     I've chosen this as it's data that I won't have to alter, I have 10 years
     of (possibly biased) data to draw from in the subreddit's spam queue.
  4. ... games? I've never been able to consistently code for this long so I 
     can't say.

## Requirements

  1. discord bot token to login to discord.
  2. a mysql database with login information to log into a db. -> currently 
     not used
  3. A redis database for the user system. -> currently used.
  4. a bot setup for reddit if you want to use the main portion of the bot
  5. a python 3.7+ install with the libs specified in the requirements.txt

## Instructions

  Realistically, there are currently too many hardcoded in constants related to
  the WiiHacks subreddit guild for this to work on any other server. Once I 
  know I can maintain a programming stride on this bot, I will eventually 
  start decoupling the cogs one at a time for use on any generic bot with met 
  requirements.

  1. Get this repo onto the place you want to run it from.
  2. Set your discord token in your environment variables:
  `DISCORD_BOT_TOKEN=put_your_token_here`
  3. Run the main script: `python3 ./wiihacky`

  Currently all configs are saved to redis. No redis access means no 
  persistence in anything.

We're licensed under MIT, and would also like to give credit to the Python
 Discord Bot : https://github.com/python-discord/bot
 
... where some of the code for this bot was both inspired by and copied from.
