import time
from threading import Thread
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import eventlet
import urllib2
import json
from flask import jsonify
from flask import request
import twitter
from apiclient import discovery
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
import httplib2
import os
import datetime

from oauth2client.client import OAuth2WebServerFlow


# stuff needed for authentication google calendar
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API SMART MIRROR'
user_gcal = 'jbird'

# jank as fuck dictionary to hold usernames and passwords
profiles = dict()
current_rfid = None

# setup Twitter api
twitter_api = twitter.Api(consumer_key='NANEOT59HbNisCUl680k9EvFz',
                      consumer_secret='kx3FPXSm004m9VAOMj8lnCx7A5UNdmQ4uh60VPL18M0YrQYPzN',
                      access_token_key='275410740-6Bsxpm2yY0peqgwEUzvN4df8f466WIXIAmvtZceh',
                      access_token_secret='ZYafFJtR8JXY4PsMYQCyRT4piYkP2xwEjFg2IPgzwHc9b')


# lol why is this needed
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

CLIENT_ID = "767898770169-fqonl25jc17v7k89p5070fegsji4g6n9.apps.googleusercontent.com"
CLIENT_SECRET = "_-FwXMnuyO7_bu8kTy2EhfqR"

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    print "starting thread"
    while True:
        time.sleep(5)
        count += 1
        # socketio.emit('response', {'data': 'Server generated event', 'count': count})

thread = Thread(target=background_thread)
thread.start()

@app.route('/')
def index():
    return render_template('index.html')

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
    username = 'CNN'
    statuses = twitter_api.GetUserTimeline(screen_name=username)
    status_msgs = [s.text for s in statuses]

    return jsonify(username=username, statuses=status_msgs)

@app.route('/login')
def login():
    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope='https://www.googleapis.com/auth/calendar',
            redirect_uri='http://localhost:5000/oauth2callback',
            approval_prompt='force',
            access_type='offline')

    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)

@app.route('/oauth2callback')
def oauth2callback():
    global credentials
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
    credentials = creds
    return redirect(url_for('index'))

# sign up page stuff
#@app.route('/signup')
#def signup():
#    return render_template('signup.html')

@app.route('/register')
def register():
    global profiles
    prof_dict = dict()
    return render_template('signup_complete.html')

#google calendar stuff
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

@app.route('/calendar')
def calendar():
    global credentials
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
    app.run(host='0.0.0.0', port=80, debug=True)
