#!/usr/bin/python
from twisted.internet import task
from twisted.internet import reactor
import shutil
import argparse
import json
import sys
import time
import datetime
import wiringpi
from flask import Flask
from threading import Thread

# TODO Create argparse method
# TODO Handle environment variables

# Delay for auto logger, in seconds
AUTOLOGGER_DELAY = 5

# Constants defining environments.
PROD = "prod"
LOCAL = "local"
NOPI = "nopi"

env = "nopi" # by default

## Ensure env arg is included.
argc = len(sys.argv)
if argc == 2:
    env = sys.argv[1]
else:
    print "Please provide environment arg."
    quit()

# Set up pins, if using Pi
if env == PROD or env == LOCAL:
    WP_PIN = 7 # See where this maps to on an rpi2
    INPUT_MODE = 0
    OUTPUT_MODE = 1
    wiringpi.wiringPiSetup() # Use wiringpi pin layout
    wiringpi.pinMode(WP_PIN, INPUT_MODE)
    time.sleep(1) # Mandatory sleep time to allow Pi to prepare for IO

# Gets door state and timestamp, returning as a tuple.
def getDoorState():
    timeStamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    doorIsOpen = "null"
    if env == NOPI:
        doorIsOpen = "true"
    elif env == PROD or env == LOCAL:
        isOpen = wiringpi.digitalRead(WP_PIN)
        doorIsOpen = "true" if isOpen is 1 else "false"
    return (timeStamp, doorIsOpen)

# Save door state to log file.
def logDoorState(timeStamp, doorState):
    with open("log.tsv", "a") as logFile:
        logFile.write(timeStamp + '\t' + doorState + '\n')
        print "Logging: " + timeStamp + '\t' + doorState + '\n'

# Script that rotates all the old logs.
def rotateLogs():
    fileNumToMove = 6
    for num in range(1,6):
        print num

# Thread for doing continuous logging.
def loggerThread():
    while True:
        val = getDoorState()
        logDoorState(val[0],val[1])
        time.sleep(AUTOLOGGER_DELAY)

# Flask setup
app = Flask(__name__)

##### REST endpoints#####

# GET call for door
@app.route("/door")
def doorIsOpen():
    doorTuple = getDoorState()
    timeStamp = doorTuple[0]
    doorIsOpen = doorTuple[1]
    json_data = { 'isOpen' : doorIsOpen,'timeStamp' : timeStamp }
    json_data = json.dumps(json_data, sort_keys=True,indent=4, separators=(',', ': '))
    return json_data

# Runs the REST server and begins auto logging
if __name__ == "__main__":
    autoLogger = Thread(target = loggerThread, args = ())
    autoLogger.start()
    app.run()
