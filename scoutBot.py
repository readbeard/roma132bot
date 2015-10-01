#!/usr/bin/python2
#
# roma132bot
# Sono il bot del gruppo scout Rm 132. Sono progettato
# per rispondere alle domande riguardo gli appuntamenti
# del gruppo! Digita una domanda chiamandomi 'scoutbot'
# ed io ti rispondero' tempestivamente! Ad esempio: 
# "scoutbot, quali sono i prossimi appuntamenti?"

from __future__ import print_function
import logging
import telegram
import random
import datetime
from datetime import datetime as dt
import httplib2
import os

from telegram import TelegramError
import re
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
LAST_UPDATE_ID = None

"""	Gets valid user credentials from storage.
	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.
	Returns:
	        Credentials, the obtained credential.	"""    
def get_credentials():
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

"""	Shows basic usage of the Google Calendar API.
	Creates a Google Calendar API service object and outputs a list of the next
	10 events on the user's calendar.	"""

def getNextEvents():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)

	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    
	#just log what you're doing...
	print('Getting the upcoming 10 events')
	
	#getting our calendar's ID from another file...
	calendar_file = open('scoutBot.conf','r')
	calendar_string = ""
	i = 1
	for line in calendar_file:
		if i == 2:
			calendar_string+= line
		i+=1
	print(calendar_string)
	#Passing roma132 calendar's ID and retrieving a list of the next 'maxResults' events..
	eventsResult = service.events().list(
        calendarId= calendar_string, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
	events = eventsResult.get('items', [])
   
	#creating string representing next events, new line for each event...
	nextEvents=""
   
	if not events:
        	print('No upcoming events found.')
   
	for event in events:

		start = {'dateTime': event['start'].get('dateTime', event['start'].get('dateTime'))}
		end = {'dateTime':  event['end'].get('dateTime',event['end'].get('date'))}

		s = datetime.datetime.strptime(start['dateTime'],"%Y-%m-%dT%H:%M:%S+02:00")
		e = datetime.datetime.strptime(end['dateTime'],"%Y-%m-%dT%H:%M:%S+02:00")

		nextEvents+= event['summary'] + ": IL GIORNO: {} ALLE ORE: {}".format(s.date().strftime( "%Y/%m/%d"),s.time().strftime( "%I:%M %p"))+", PRESSO: " + event['location'] + "\n"
		nextEvents+= " e si concludera' " + "IL GIORNO: {} ALLE ORE: {}".format(e.date().strftime( "%Y/%m/%d"),e.time().strftime( "%I:%M %p")) + "\n\n"
	
	return nextEvents;

"""	Reads from a file named "catena" the information about scout chief
	of the group, such as telephone numbers, emails and so on
	Returns:
		a string with the content of the file, line per line.	 """

def getInfosFromFile():
	infos_file = open('catena','r')
	infos_string = ""

	for line in infos_file:
		infos_string += line

	infos_file.close()

	return infos_string

def main():
	global LAST_UPDATE_ID

	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# Load the authorization token
	with open('scoutBot.conf', 'r') as f:
		token_string = f.readline().rstrip()

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

			# Check if the user is talking to me
			if not message.startswith('scoutbot'):
				continue

			# Remove my name from message and leading spaces
			message = message[9:].lstrip()

			# Check for specific commands
			if re.match('.*parola maestra.*',message):
				reply+= generateRandomJungleWord()
			elif re.match('.*appuntamenti.*',message) or re.match('.*riunione.*', message) or re.match('.*uscita.*', message):
				reply+= getNextEvents()
			elif re.match(".*contatti.*", message):
				reply+= getInfosFromFile()
			else:
				reply+= "come?"	
		try:
			bot.sendMessage(chat_id=chat_id, text=reply.encode('utf-8'))
		except TelegramError, e:
			print(e)

if __name__ == '__main__':
    main()
