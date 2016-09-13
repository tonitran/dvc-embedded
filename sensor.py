#!/usr/bin/python3
# Python 3.5.2

from crochet import setup, wait_for, run_in_reactor
from flask import Flask
from pprint import pprint
from threading import Thread
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.task import LoopingCall
import argparse
import datetime
import json
import shutil
import sqlite3
import sys
import time
import wiringpi

# Run Crochet setup to allow Twisted runs during Flask
setup()

# TODO Create argparse method
# TODO Handle environment variables
# Log only at certain times

################################################################################
# RUN CONFIGS
################################################################################
# Delay for auto logger, in seconds
env = "nopi" # by default

################################################################################
# ENVIRONMENT VARIABLES
################################################################################

# Constants defining environments.
PROD = "prod"
LOCAL = "local"
NOPI = "nopi"


## Ensure env arg is included.
argc = len(sys.argv)
if argc == 2:
    env = sys.argv[1]
else:
    print("Please provide environment arg.")
    quit()

################################################################################
# PI HARDWARE
################################################################################

# Set up pins, if using Pi
if env == PROD or env == LOCAL:
    WP_PIN = 7 # See where this maps to on an rpi2
    INPUT_MODE = 0
    OUTPUT_MODE = 1
    wiringpi.wiringPiSetup() # Use wiringpi pin layout
    wiringpi.pinMode(WP_PIN, INPUT_MODE)
    time.sleep(1) # Mandatory sleep time to allow Pi to prepare for IO

# Gets door state and timestamp, returning as a dict.
# The DateTime object is always in the form of YYYY-MM-DD. (0 Padded)
def getDoorState():
    timeStamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    doorIsOpen = -1
    if env == NOPI:
        doorIsOpen = 0
    elif env == PROD or env == LOCAL:
        isOpen = wiringpi.digitalRead(WP_PIN)
        doorIsOpen = isOpen
    return {'timeStamp': timeStamp, 'isOpen': doorIsOpen}

################################################################################
# LOGGING AND SQLITE
################################################################################

def accessDB(method, vals):
    if method == 'log':
        pass
    elif method == 'query':
        pass

# Save door state to log file.
def logDoorState(dict):
    con = None
    try:
        con = sqlite3.connect('logs.db')
        cur = con.cursor()
        val = (dict['timeStamp'], dict['isOpen'])
        print(val)
        cur.execute('insert into history (timeStamp, isOpen) values (?,?)', val)
        con.commit()
    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if con:
            con.close()

# Crochet thread that manages and runs auto logging.
# TODO Plugging holes in DB?
@run_in_reactor
def loggerThread():
    #Wait for an even 5th minute to begin logging.
    currMin = -1
    while (currMin % 5) != 0:
        now = datetime.datetime.now()
        currMin = now.minute
    while True:
        print("Logging auto")
        state = getDoorState()
        logDoorState(state)
        time.sleep(60 * 5)

################################################################################
# FLASK
################################################################################

# Flask setup
app = Flask(__name__)

##### REST endpoints#####

def dictListToJSON(item):
    json_data = json.dumps(item, sort_keys=True, separators=(',', ':'))
    return json_data

# GET call for door
@app.route("/door")
def doorIsOpen():
    doorStateDict = getDoorState()
    json_data = json.dumps(doorStateDict, sort_keys=True, separators=(',', ':'))
    return json_data

@app.route('/logs/<string:year>/<string:month>/<string:day>')
def getLog(year, month, day):
    # TODO Sanitize input using cursor function.
    date = "%s-%s-%s" % (year, month, day)
    con = None
    try:
        con = sqlite3.connect('logs.db')
        cur = con.cursor()
        cur.execute('select * from history where DATE(timeStamp) = ?', (date,))
        returnList = cur.fetchall()

        #Construct the list for the json encoder.
        listToEncode = []
        for tuple in returnList:
            jsonDict = {'timeStamp': tuple[0], 'isOpen': tuple[1]}
            listToEncode.append(jsonDict)

        #Encode the JSON
        json_data = json.dumps(listToEncode, sort_keys=False, separators=(',', ':'))
        return json_data

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if con:
            con.close()

# Runs the REST server and begins auto logging
if __name__ == "__main__":
    loggerThread()
    app.run()
