#!/usr/bin/python3
# Python 3.5.2

from runConfigs import *
from crochet import setup, wait_for, run_in_reactor
from flask import request
from flask import Flask
from flask_cors import CORS, cross_origin
from pprint import pprint
from threading import Thread
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.task import LoopingCall
import argparse
import datetime
import json
import random
import shutil
import sqlite3
import sys
import time
import wiringpi

# Run Crochet setup to allow Twisted runs during Flask
setup()

################################################################################
# PI HARDWARE
################################################################################

# Set up pins, if using Pi
if ENV != NOPI:
    WP_PIN = 7 # See where this maps to on an rpi2
    INPUT_MODE = 0
    OUTPUT_MODE = 1
    wiringpi.wiringPiSetup() # Use wiringpi pin layout
    wiringpi.pinMode(WP_PIN, INPUT_MODE)
    time.sleep(1) # Mandatory sleep time to allow Pi to prepare for IO

# Gets door state and timestamp, returning as a dict.
# The DateTime object is always in the form of YYYY-MM-DD. (0 Padded)
def getDoorState():
    timeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    doorIsOpen = -1
    if ENV == NOPI:
        doorIsOpen = random.randint(0, 1) # If no pi, generate random data
    elif ENV == PROD or ENV == LOCAL:
        isOpen = wiringpi.digitalRead(WP_PIN)
        doorIsOpen = isOpen
    return {'timeStamp': timeStamp, 'isOpen': doorIsOpen}

################################################################################
# LOGGING AND SQLITE
################################################################################

def accessDB(operation, query, vals):
    # TODO Sanitize input before feeding to cursor.execute substitution

    con = None
    try:
        con = sqlite3.connect('/var/www/dvc-flask-app.com/logs.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(query, vals)
        if operation == 'SELECT':
            return cur.fetchall()
        if operation == 'INSERT':
            con.commit()
    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if con:
            con.close()

# Save door state to log file.
def logDoorState(dict):
    val = (dict['timeStamp'], dict['isOpen'])
    query = 'insert into history (timeStamp, isOpen) values (?,?)'
    accessDB('INSERT', query, val)
    print("Logged: " + str(val))

# Crochet thread that manages and runs auto logging.
@run_in_reactor
def loggerThread():

    PROD_INTERVAL = 60 * 5 # seconds
    PROD_START_MOD = 5 # Start on next minute evenly divisible by x
    LOCAL_INTERVAL = 5 # seconds
    LOCAL_START_MOD = 1 # Start on next nth minute.

    START_MOD = PROD_START_MOD if ENV == PROD else LOCAL_START_MOD
    INTERVAL = PROD_INTERVAL if ENV == PROD else LOCAL_INTERVAL

    currMin = -1
    while (currMin % START_MOD) != 0:
        now = datetime.datetime.now()
        currMin = now.minute
    while True:
        state = getDoorState()
        logDoorState(state)
        time.sleep(INTERVAL)

################################################################################
# FLASK
################################################################################

# Flask setup
if loggingEnabled is True:
    loggerThread() #Run logger before starting application.
app = Flask(__name__)
CORS(app) #Run with server enabled CORS

##### REST endpoints#####

# Converts a dict or list to JSON
def convertToJSON(item):
    json_data = json.dumps(item, sort_keys=True, separators=(',', ':'))
    return json_data

# GET call for door
@app.route("/door")
@cross_origin()
def doorIsOpen():
    doorStateDict = getDoorState()
    return convertToJSON(doorStateDict)

@app.route('/logs/<string:year>/<string:month>/<string:day>')
@cross_origin()
def getLogOn(year, month, day):

    #Make the query
    query = 'select * from history where DATE(timeStamp) = ?-?-?'
    returnList = accessDB('SELECT',query,(year,month,day))

    #Construct the list for the json encoder.
    listToEncode = []
    for tuple in returnList:
        jsonDict = {'timeStamp': tuple[0], 'isOpen': tuple[1]}
        listToEncode.append(jsonDict)

    #Encode the JSON
    return convertToJSON(listToEncode)

@app.route('/logs')
@cross_origin()
def getLogRange():

    lowerBound = request.args.get('from')
    upperBound = request.args.get('to')

    query = 'select * from history where timeStamp >= ? and timeStamp < ?'
    returnList = accessDB('SELECT',query,(lowerBound,upperBound))

    #Construct the list for the json encoder.
    listToEncode = []
    for tuple in returnList:
        jsonDict = {'timeStamp': tuple[0], 'isOpen': tuple[1]}
        listToEncode.append(jsonDict)

    #Encode the JSON
    return convertToJSON(listToEncode)
