# scoutbot
Welcome to the first bot created to manage the scout group of Rm 132! It will reply (for now) to your questions about
next appointments and infos about the chiefs! The bot takes the events from our google calendar, and the information
about chiefs from a file called *catena*

## depencencies
To run the bot, you will need 
- the telegram module to be installed. Type `pip install python-telegram-bot` to install it
- the Google Client library for python. Type `pip install --upgrade google-api-python-client` to install it

### useful notes
There are three main files to fill with information. The first one, **scoutbot.conf**,is written in JSON and it must contain two objects: *telegram_bot_token* and *calendar_id*. It is mandatory to fill with the following informations:
- first JSONobject: your telegram bot's token
- second JSONobject: the calendar's id of the google calendar you want to retrieve information from

The second one, *catena*, is read and printed as it is written, and it must contain the infos about scout chiefs of your group. So, you can fill it as you want, preferably in a human-readable manner.

The third one, *jungle_words*, is randomly read (line per line) and i must contain, line per line, a jungle word (for more information about them, see [this](https://it.wikipedia.org/wiki/Lupetti#Le_Parole_Maestre) link, under section 'Parole Maestre', or [this](https://it.scoutwiki.org/Parola_Maestra) link. 
