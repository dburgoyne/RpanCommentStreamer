# RpanCommentStreamer
A Discord bot that can echo comments made on Reddit Public Access Network (RPAN) streams in near-real-time.

## Requirements
```
pip install asyncio discord.py nest-asyncio python-dotenv requests websockets
```
The bot was written and tested using Python 3.7. It may or may not work with other 3.x releases.

You should create a bot from your Discord developer portal, then create file called .env in the same folder as bot.py with the following contents:
```
# .env
DISCORD_TOKEN={your Discord token}
```
See https://realpython.com/how-to-make-a-discord-bot-python/#creating-a-discord-connection for more details.

## Starting the bot
After adding the bot to your channel, just run
```
python ./bot.py
```
to start the bot. CTRL-C quits (may take a few seconds since it tries to gracefully shut down the async loops). You may want to run it on a VPS to keep it running continuously.

## Using the bot
Type `!rcs help` in your Discord channel to see a list of available commands and what they do.

## Limitations
The bot uses a single set of global variables to maintain state. Each instance of the bot should run in **only one server at a time** and the bot's state will reset when the bot is restarted. Replacing these variables with threadsafe dictionaries keyed on server/channel, or with an appropriately-designed database, would make it scalable.

## Contributing
There are lots of cool features you might want to add, such as automatically starting whenever a particular Reddit user starts streaming + automatically stopping when they end. Please feel free to open pull requests into this repo!
