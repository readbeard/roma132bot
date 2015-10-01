# scoutbot
Welcome to the first bot created to manage the scout group of Rm 132! It will reply (for now) to your questions about
next appointments and infos about the chiefs! The bot takes the events from our google calendar, and the information
about chiefs from a file called *catena*

## depencencies
To run the bot, you will need 
- the telegram module to be installed. Type `pip install python-telegram-bot` to install it
- the Google Client library for python. Type `pip install --upgrade google-api-python-client` to install it

### useful notes
There are two main files to fill with information. The first one, *scoutbot.conf*, is mandatory to fill with the following informations:
- first line: your telegram bot's ID
- second line: the calendar's id of the google calendar you want to retrieve information from
