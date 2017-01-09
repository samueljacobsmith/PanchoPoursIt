"""
Author: Samuel Jacob Smith
Written December 2016
find Pancho on twitter @panchopoursit
"""

import tweepy
import json

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

import os
import subprocess

import RPi.GPIO as GPIO
import time

import random

def toPowerSwitch(command):
    if command == True:
        print('POWER ON')
        GPIO.output(2, True)
    elif command == False:
        print('POWER OFF')
        GPIO.output(2, False)
        
class StreamListener(tweepy.StreamListener):

    mode = False
    permittedUsers = ['enter user ids here']
        
    def on_status(self, status):
        if status.retweeted:
            return
        
        if '#pourmesome' in status.text and StreamListener.mode == False and any(status.user.id == user for user in StreamListener.permittedUsers):
            StreamListener.mode = True
            toPowerSwitch(StreamListener.mode)

            cmd = 'pico2wave --lang=en-GB --wave=/tmp/test.wav '

            pourChoices = ['"Pouring out that fresh, bean juice. Do not snort the beans, for your own safety."',
               '"Good morning, human. Fun fact: if I, could be any instrument, it would be the bag pipes."',
               '"Initiating bean juice procedure. Please assume the position and await further instruction."']

            randomChoice = random.choice(pourChoices)

            subprocess.Popen(cmd + randomChoice + '; aplay /tmp/test.wav; rm /tmp/test.wav', shell = True)
            
            api.update_status(status = 'pouring out that fresh bean juice', in_reply_to_status_id = status.id_str)
            api.update_profile(description = '~**current mood: awake**~' + bio)

        elif '#thx' in status.text and StreamListener.mode == True and any(status.user.id == user for user in StreamListener.permittedUsers):
            StreamListener.mode = False
            toPowerSwitch(StreamListener.mode)
            
            cmd = 'pico2wave -w test.wav '
            
            stopChoices = ['"Mamas gotta blast. Enjoy my coffee, and remember: baby clothes are for babies"',
               '"Siesta time. Enjoy my coffee and have a great day."',
                '"I hope you enjoy my coffee, and remember: no one throws birthday parties, for coffee pots."']

            randomChoice = random.choice(stopChoices)

            subprocess.Popen(cmd + randomChoice + '; aplay /tmp/test.wav; rm /tmp/test.wav', shell = True)
            
            api.update_status(status = 'siesta time', in_reply_to_status_id = status.id_str)
            api.update_profile(description = '*~~current mood: siesta time~~*' + bio)

        elif '#talktome' in status.text:
            name = status.user.screen_name
            
            actualTweet = status.text.replace('#talktome', '')
            actualTweet = actualTweet.replace('@panchopoursit', '')      

            cmd = 'pico2wave --lang=en-GB --wave=/tmp/test.wav "Tweet from' + name + ': ' + actualTweet + '."; aplay /tmp/test.wav; rm /tmp/test.wav'
            subprocess.Popen(cmd, shell = True)
            
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            return False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)

stream_listener = StreamListener()

toPowerSwitch(stream_listener.mode)

bio = '\n I am a twitter-activated, talking coffee maker. Tweet at me with the hashtag #talktome and I will read your tweet aloud!'
api.update_profile(description = '~~current mood: siesta time~*~' + bio)

subprocess.Popen('pico2wave --lang=en-GB --wave=/tmp/test.wav "Poncho here, ready to pour."; aplay /tmp/test.wav; rm /tmp/test.wav', shell = True)

print('Scanning twitter...')

stream = tweepy.Stream(auth = api.auth, listener = stream_listener)
stream.filter(track = ['panchopoursit'])
