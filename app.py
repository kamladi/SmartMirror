import time
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import eventlet
import urllib2
import json
from flask import jsonify
import twitter
from apiclient import discovery
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
import httplib2
import os
import datetime
import usr_dct

# stuff needed for authentication google calendar
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API SMART MIRROR'
user_gcal = 'jbird'

# setup Twitter api
twitter_api = twitter.Api(consumer_key='NANEOT59HbNisCUl680k9EvFz',
                      consumer_secret='kx3FPXSm004m9VAOMj8lnCx7A5UNdmQ4uh60VPL18M0YrQYPzN',
                      access_token_key='275410740-6Bsxpm2yY0peqgwEUzvN4df8f466WIXIAmvtZceh',
                      access_token_secret='ZYafFJtR8JXY4PsMYQCyRT4piYkP2xwEjFg2IPgzwHc9b')


eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    print "starting thread"
    while True:
        time.sleep(5)
        count += 1
        #socketio.emit('response', {'data': 'Server generated event', 'count': count})

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
    print parsed_json
    location = parsed_json['current_observation']['display_location']['city']
    temp_f = parsed_json['current_observation']['temp_f']
    f.close()
    return jsonify(location=location, temperature=temp_f)


@app.route('/twitter')
def twitter():
    statuses = twitter_api.GetUserTimeline(screen_name='CNN')
    status_msgs = [s.text for s in statuses]
    return jsonify(statuses=status_msgs)

#google calendar stuff
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None



def gcal_get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials.', user_gcal)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-smart-mirror.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6                                      
            credentials = tools.run(flow, store)
    return credentials

@app.route('/calendar')
def calendar():
    credentials = gcal_get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time                    
    print('Getting the upcoming 5 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    return

    
@socketio.on('connect')
def test_connect():
    print 'client connected'

@socketio.on('disconnect')
def test_disconnect():
    print 'Client disconnected'

@socketio.on('my broadcast event')
def broadcast_event(msg):
    print 'broadcast msg yo: ', msg['data']

if __name__ == "__main__":
    # socketio.run(app)
    app.run(debug=True)
