#!/usr/bin/env python

"""
Modified play_audio demo from the pyspotify source

Loads a random song from Spotify's 'Today's Top Hits' playlist

Supports button presses for:
    > previous track
    > next track
    > pause

*******************************************************************************

Information from play_audio.py

This is an example of playing music from Spotify using pyspotify.

The example use the :class:`spotify.AlsaSink`, and will thus only work on
systems with an ALSA sound subsystem, which means most Linux systems.

You can either run this file directly without arguments to play a default
track::

    python play_track.py

Or, give the script a Spotify track URI to play::

    python play_track.py spotify:track:3iFjScPoAC21CT5cbAFZ7b

"""

from __future__ import unicode_literals

import sys
import threading
import random
import time
import RPi.GPIO as GPIO

import spotify

#set up Raspberry Pi GPIO pins

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#global variables for keeping track of tracks
session = None
end_of_track = None
logged_in = None
# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()
playlist = None
curSong = 0 #global track number
length = 0 #global length of tracklist




def playSong():
    global session
    global length
    global playlist
    global curSong
    if playlist.is_loaded:
        track = playlist.tracks[curSong].load()
        session.player.load(track)
        session.player.play()


def on_connection_state_updated(session):
    global logged_in
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    global end_of_track
    end_of_track.set()




def initialize():
	global session
	global logged_in
	global playlist
	global length
	config = spotify.Config()
	config.user_agent = 'smart'
#	config.tracefile = b'/tmp/libspotify-trace.log'
	#if sys.argv[1:]:
	#    track_uri = sys.argv[1]
	#else:
	#    track_uri = 'spotify:track:6xZtSE6xaBxmRozKA0F6TA'

	# Assuming a spotify_appkey.key in the current dir

	session = spotify.Session(config)
	session.login('johnwbird', 'bitterjava60', True)
	# Process events in the background
	loop = spotify.EventLoop(session)
	loop.start()

	# Connect an audio sink
	audio = spotify.AlsaSink(session)

	# Register event listeners 
	session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
	session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

	# Assuming a previous login with remember_me=True and a proper logout
	#session.relogin()

	logged_in.wait()

	playlist = session.get_playlist('spotify:user:spotify:playlist:5FJXhjdILmRA2z5bvz4nzf')
	playlist.load().name
	length = len(playlist.tracks)
	random.seed()
	curSong = random.randint(0, length-1)


	# Play from the billboard top playlist, sketch shuffle style

def nextSong():
	global curSong
	global length
	curSong = (curSong + 1) % length
	session.player.pause()
	playSong()

def prevSong():
	global curSong
	global length
	curSong = (curSong - 1) % length	
	session.player.pause()
	playSong()

def playPause():
	if (session.player.state == spotify.PlayerState.PLAYING):
		session.player.pause()
	else:
		session.player.play()

