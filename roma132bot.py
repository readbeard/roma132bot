#!/usr/bin/python2
#
# roma132bot
# Sono il bot del gruppo scout Rm 132. Sono progettato
# per rispondere alle domande riguardo gli appuntamenti
# del gruppo! Digita una domanda chiamandomi 'roma132bot'
# ed io ti rispondero' tempestivamente! Ad esempio:
# "roma132bot, quali sono i prossimi appuntamenti?"

from __future__ import print_function
import logging
import telegram
import random
import datetime
from datetime import datetime as dt
import httplib2
import os
from config_utils import load_configs
from telegram import TelegramError
import re
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

LAST_UPDATE_ID = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
	"""Gets valid user credentials from storage.
	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.	"""

	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')

	if not os.path.exists(credential_dir):
		 os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,'calendar-quickstart.json')

	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()

	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME

		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatability with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)

	return credentials


def getNextEvents(calendar_id):
	"""Shows basic usage of the Google Calendar API.
	Creates a Google Calendar API service object and outputs a list of the next
	10 events on the user's calendar.	"""

	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)

	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	#just log what you're doing...
	print('Getting the upcoming 10 events')

	#Passing roma132 calendar's ID and retrieving a list of the next 'maxResults' events..
	eventsResult = service.events().list(calendarId=calendar_id, timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
	events = eventsResult.get('items', [])

	#creating string representing next events, new line for each event...
	nextEvents=""

	if not events:
   		nextEvents += 'No upcoming events found'
	for event in events:

		start = {'dateTime': event['start'].get('dateTime', event['start'].get('dateTime'))}
		end = {'dateTime':  event['end'].get('dateTime',event['end'].get('date'))}

		s = datetime.datetime.strptime(start['dateTime'],"%Y-%m-%dT%H:%M:%S+02:00")
		e = datetime.datetime.strptime(end['dateTime'],"%Y-%m-%dT%H:%M:%S+02:00")

                delimiter = '---------------------------------------------------------------------\n'
                nextEvents+= event['summary'] + ": *IL GIORNO:* _{}_ *ALLE ORE:* _{}_".format(s.date().strftime( "%Y/%m/%d"),s.time().strftime( "%I:%M %p"))+", *PRESSO:* " + event.get('location',"non definito...") + "\n"
		nextEvents+= " e si concludera' " + "*IL GIORNO:* _{}_ *ALLE ORE:* _{}_".format(e.date().strftime( "%Y/%m/%d"),e.time().strftime( "%I:%M %p")) + "\n"+delimiter
	return nextEvents;

def help_message():
        message ="Ciao! sono il bot del gruppo scout Rm132. Digita una tra le seguenti parole, in una frase a tuo piacimento che inizi con la parola chiave _roma132bot_, ed io ti rispondero' adeguatamente! (Oppure, digita _/_ e segui i suggerimenti)"
        parolaMaestra = "*parola maestra* --- stampa una randomica parola maestra"
        appuntamenti = "*uscita*, *riunione*, *appuntamenti* --- stampa i prossimi appuntamenti del gruppo"
	contatti = "*contatti* --- stampa i contatti dei capi del gruppo"
        commands = (parolaMaestra, appuntamenti, contatti)
        commands_str = reduce(lambda x,y: x + "\n" + y, commands)
        return "{}\n\n{}\n".format(message, commands_str)

def getInfosFromFile():
	"""Reads from a file named "catena" the information about scout chief
	of the group, such as telephone numbers, emails and so on

	Returns:
		a string with the content of the file, line per line.
	"""
	with open('catena', 'r') as f:
		return reduce(lambda x,y: x+y, f)

def main():
	global LAST_UPDATE_ID

	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	global calendar_id
	config_default = {'telegram_bot_token': None,
			  'calendar_id': None}
	conf = load_configs(envvar_prefix="SB_", path='roma132bot.conf', defaults=config_default)

	# Load the authorization token
	token_string = conf['telegram_bot_token']
	calendar_id = conf['calendar_id']

	# Telegram Bot Authorization Token
	bot = telegram.Bot(token_string)

	# This will be our global variable to keep the latest update_id when requesting
	# for updates. It starts with the latest update_id if available.
	try:
		LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
	except IndexError:
		LAST_UPDATE_ID = None

	while True:
		process(bot)

def generateRandomJungleWord():
	jungle_file = open('jungle_words','r')
	lines = jungle_file.read().splitlines()
	return random.choice(lines)

def process(bot):
	global LAST_UPDATE_ID

	# Request updates after the last updated_id
	for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
	# chat_id is required to reply any message
		chat_id = update.message.chat_id
		username = update.message.from_user
		message = update.message.text.lower()
		reply = ""
		if (message):
			# Updates global offset to get the new updates
			LAST_UPDATE_ID = update.update_id + 1

                        #Check if a command is requested
                        if message.startswith('/'):
                            #remove '/' character
                            command = message[1:]
                            if command == "help" or command== "help@roma132bot":
                                reply+=help_message()
                            elif command == "parolamaestra" or command== "parolamaestra@roma132bot":
                                reply+= generateRandomJungleWord()
                            elif command == "contatti" or command == "contatti@roma132bot":
                                reply+= getInfosFromFile()
                            elif command == "appuntamenti" or command == "appuntamenti@roma132bot":
                                reply+= getNextEvents(calendar_id)
                            else:
                        	reply+= "scusa, non ho capito cosa mi hai scritto :("

                        #Check if human is talking to me
                        elif message.startswith('roma132bot'):
				# Remove my name from message and leading spaces
				message = message[9:]

				# Check for specific commands
				if re.match('.*(parola maestra).*',message):
					reply+= generateRandomJungleWord()
				elif re.match('.*(appuntamenti|riunione|uscita).*',message):
					reply+= getNextEvents(calendar_id)
				elif re.match(".*contatti.*", message):
					reply+= getInfosFromFile()
                                elif re.match("/help",message):
                                        reply+=help_message()
				else:
					reply+= "scusa, non ho capito cosa mi hai scritto :("
			try:
                            if reply:
                                bot.sendMessage(chat_id=chat_id, text=reply.encode('utf-8'),parse_mode ="Markdown")
			except TelegramError, e:
			    print(e)

if __name__ == '__main__':
    main()
