
import time
from threading import Thread
from flask import Flask, session, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import eventlet
import urllib2
import json
from flask import jsonify
from flask import request
from flask.ext.qrcode import QRcode
import twitter
from apiclient import discovery
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
import httplib2
import os
import datetime
import binascii
import sys
import Adafruit_PN532 as PN532
from oauth2client.client import OAuth2WebServerFlow
import RPi.GPIO as GPIO
from smartspotify.play_track import initialize, playSong, nextSong, prevSong, getCurrentSongInfo, playPause


# stuff needed for authentication google calendar
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API SMART MIRROR'

#GPIO Setup
GPIO.setmode(GPIO.BCM)
BTN_PREV = 5
BTN_PAUSE = 12
BTN_NEXT = 26
BTN_QR = 21

GPIO.setup(BTN_PREV, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_QR, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# jank as fuck dictionary to hold usernames and passwords
profiles = dict()
usr_0 = '04a577726d4880'
current_rfid = usr_0
other_usr_1 = '04bef4726d4880'
other_usr_2 = '04a69a726d4880'

def get_current_profile():
	global profiles
	global current_rfid
	return profiles[current_rfid]

# setup basic structure for user profile settings
profiles[current_rfid] = {
	'twitter_username': 'CNN',
	'google_credentials': None,
	'reminders': []
}
profiles[other_usr_1] = {
	'twitter_username': 'nytimes',
	'google_credentials': None,
	'reminders': []
}
profiles[other_usr_2] = {
	'twitter_username': 'kanyewest',
	'google_credentials': None,
	'reminders': []
}

# helper function to switch users (or create new user) and trigger socket events
# to update the mirror
def switch_user(rfid):
	global current_rfid
	global profiles
	if current_rfid == rfid:
		return
	# new user, create new profile
	if rfid not in profiles:
		print "NEW USER RFID: ", rfid
		new_profile = {
			'twitter_username': 'coffeedad',
			'google_credentials': None,
			'reminders': []
		}
		profiles[rfid] = new_profile
		socketio.emit('new user', {'rfid': rfid})

	# set current user id to the given rfid
	current_rfid = rfid
	socketio.emit('update calendar', {'rfid': rfid})
	socketio.emit('update twitter', {'rfid': rfid})

# setup Twitter api
twitter_api = twitter.Api(consumer_key='NANEOT59HbNisCUl680k9EvFz',
					  consumer_secret='kx3FPXSm004m9VAOMj8lnCx7A5UNdmQ4uh60VPL18M0YrQYPzN',
					  access_token_key='275410740-6Bsxpm2yY0peqgwEUzvN4df8f466WIXIAmvtZceh',
					  access_token_secret='ZYafFJtR8JXY4PsMYQCyRT4piYkP2xwEjFg2IPgzwHc9b')

#Config for Rasp Pi
CS = 18
MOSI = 23
MISO = 24
SCLK = 25
pn532 = PN532.PN532(cs=CS, sclk =SCLK, mosi=MOSI, miso=MISO)
pn532.begin()
pn532.SAM_configuration()

# lol why is this needed
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

CLIENT_ID = "767898770169-fqonl25jc17v7k89p5070fegsji4g6n9.apps.googleusercontent.com"
CLIENT_SECRET = "_-FwXMnuyO7_bu8kTy2EhfqR"

# QRcode init
QRcode(app)

# Initialize Spotify Music Player
initialize()

def rfid_thread_fn():
	print "Starting rfid thread"
	while True:
		time.sleep(5)
		# Read from RFID shield
		uid = pn532.read_passive_target(timeout_sec=1)
		if uid is not(None):
			uid_string = binascii.hexlify(uid)
			print 'Found card with UIS: 0x{0}'.format(uid_string)
			switch_user(uid_string)


def buttons_thread_fn():
	print "Starting buttons thread"
	while True:
		time.sleep(0.1)
		# Read buttons
		btn_prev_in = GPIO.input(BTN_PREV)
		btn_pause_in = GPIO.input(BTN_PAUSE)
		btn_next_in = GPIO.input(BTN_NEXT)
		btn_qr_in = GPIO.input(BTN_QR)

		# respond to possible buttons being pressed
		if not btn_prev_in:
			prevSong()
			socketio.emit('new song', getCurrentSongInfo())
			time.sleep(0.3)
		if not btn_pause_in:
			playPause()
			time.sleep(0.3)
		if not btn_next_in:
			nextSong()
			socketio.emit('new song', getCurrentSongInfo())
			time.sleep(0.3)
		if not btn_qr_in:
			socketio.emit('toggle qr', {});
			time.sleep(0.3)

rfid_thread = Thread(target=rfid_thread_fn)
rfid_thread.start()

buttons_thread = Thread(target=buttons_thread_fn)
buttons_thread.start()



@app.route('/')
def index():
	return render_template('index.html', {
			qr_string="dankmirror.wv.cc.cmu.edu/settings"
		})


@app.route('/qr')
def qr():
	qr_display = 1
	#if (current_rfid in profiles)
		#qr_display = 0
	return jsonify(line=render_template('qr.html',
		qr_string="dankmirror.wv.cc.cmu.edu/settings"),
		display=qr_display)

@app.route('/funsies')
def funsies():
	 socketio.emit('update calendar', {'data': 'Server generated event'})
	 socketio.emit('update twitter', {'data': 'Server generated event'})
	 return ''

@app.route('/weather')
def weather():
	API_KEY = 'f31628e0ca22e208'
	URL = 'http://api.wunderground.com/api/' + API_KEY + '/conditions/q/PA/Pittsburgh.json'
	f = urllib2.urlopen(URL)
	json_string = f.read()
	parsed_json = json.loads(json_string)
	current_observation = parsed_json['current_observation']

	result = {
		'location': current_observation['display_location']['city'],
		'temperature': current_observation['temp_f'],
		'weather_desc': current_observation['weather'],
		'icon_url': current_observation['icon'],
		'icon_url': current_observation['icon_url']
	}

	f.close()
	return jsonify(**result)


@app.route('/twitter')
def twitter():
	username = get_current_profile()['twitter_username']
	if username is None:
		username = 'CNN'
	statuses = twitter_api.GetUserTimeline(screen_name=username)
	status_msgs = [s.text for s in statuses]

	return jsonify(username=username, statuses=status_msgs)

@app.route('/google/login')
def google_login():
	flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
			client_secret=CLIENT_SECRET,
			scope='https://www.googleapis.com/auth/calendar',
			redirect_uri='http://dankmirror.wv.cc.cmu.edu/google/oauth2callback',
			approval_prompt='force',
			access_type='offline')

	auth_uri = flow.step1_get_authorize_url()
	return redirect(auth_uri)

@app.route('/google/logout')
def google_logout():
	current_user = get_current_profile()
	current_user['google_credentials'] = None
	return redirect(url_for('settings'))

@app.route('/google/oauth2callback')
def oauth2callback():
	global credentials
	global current_rfid
	code = request.args.get('code')
	if code:
		flow = OAuth2WebServerFlow(CLIENT_ID,
					CLIENT_SECRET,
					"https://www.googleapis.com/auth/calendar")
		flow.redirect_uri = request.base_url
		try:
			creds = flow.step2_exchange(code)
		except Exception as e:
			print "Unable to get an access token because ", e.message
	current_user = get_current_profile()
	current_user['google_credentials'] = creds
	socketio.emit('update calendar', {'rfid', current_rfid})
	return redirect(url_for('settings'))

# sign up page stuff
@app.route('/settings')
def settings():
	current_user = get_current_profile()
	google_credentials = current_user['google_credentials']
	google_logged_in = False
	if google_credentials and google_credentials.invalid is False:
		google_logged_in = True
	twitter_username = current_user['twitter_username']
	return render_template('settings.html', google_logged_in=google_logged_in, twitter_username=twitter_username)

#google calendar stuff
try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

@app.route('/settings/twitter', methods=['POST'])
def twitter_settings():
	global current_rfid
	current_user = get_current_profile()
	request_twitter_username = request.form['twitter_username']
	if request_twitter_username is None:
		return redirect(url_for('settings'))

	# remove '@' from beginning of username
	request_twitter_username = request_twitter_username.replace('@','')
	current_user['twitter_username'] = request_twitter_username
	socketio.emit('update twitter', {'rfid', current_rfid})
	session.message = "successfully updated twitter username"
	return redirect(url_for('settings'))


@app.route('/calendar')
def calendar():
	credentials = get_current_profile()['google_credentials']
	if credentials is None or credentials.invalid:
		return jsonify(events=[]), 404
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)
	eventList = []

	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	laterTime = datetime.datetime.utcnow()+ datetime.timedelta(days=1)
	later = laterTime.isoformat() + 'Z'

  #  print('Getting the upcoming 5 events')
	eventsResult = service.events().list(
		calendarId='primary', timeMin=now, timeMax =later, maxResults=5, singleEvents=True,
		orderBy='startTime').execute()
	events = eventsResult.get('items', [])

	for event in events:
		result = {
			'start' : event['start'].get('dateTime', event['start'].get('date')),
			'title' : event['summary']
		 }
		eventList.append(result)
	return jsonify(events=eventList)


@socketio.on('connect')
def test_connect():
	print 'client connected'

@socketio.on('disconnect')
def test_disconnect():
	print 'Client disconnected'

if __name__ == "__main__":
	# socketio.run(app)
	socketio.run(app,host='0.0.0.0', port=80, debug=True)
