from flask import request
from crochet import setup, wait_for, run_in_reactor
setup() # Run Crochet setup to allow Twisted runs during Flask
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
import yaml

################################################################################
# SETUP
################################################################################
global ENV
global START_MOD
global INTERVAL
global LOGGING_ENABLED
with open('/var/www/dvc-flask-app.com/config.yaml','r') as config:
    doc = yaml.load(config)
    ENV = doc['environment']
    START_MOD = doc['environments'][ENV]['logPoint']
    INTERVAL = doc['environments'][ENV]['logInterval']
    LOGGING_ENABLED = doc['loggingEnabled']

# Set up pins, if using Pi
if ENV != 'nopi':
    WP_PIN = 4 # GPIO pin 4 = wiringpi pin 7 on an RPI2B+
    INPUT_MODE = 0
    OUTPUT_MODE = 1
    wiringpi.wiringPiSetupSys()

# Crochet thread that manages and runs auto logging.
@run_in_reactor
def loggerThread():
    currMin = -1
    while (currMin % START_MOD) != 0:
        now = datetime.datetime.now()
        currMin = now.minute
    while True:
        state = getDoorState()
        logDoorState(state)
        time.sleep(INTERVAL)

if LOGGING_ENABLED is True:
    loggerThread() #Run logger before starting application.

################################################################################
# HARDWARE INTERACTIONS
################################################################################
# Gets door state and timestamp, returning as a dict.
# The DateTime object is always in the form of YYYY-MM-DDTHH:MM:SS. (0 Padded)
def getDoorState():
    timeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    doorIsOpen = -1
    if ENV == 'nopi':
        doorIsOpen = random.randint(0, 1) # If no pi, generate random data
    elif ENV == 'prod' or ENV == 'local':
        isOpen = wiringpi.digitalRead(WP_PIN)
        doorIsOpen = isOpen
    return {'timeStamp': timeStamp, 'isOpen': doorIsOpen}

################################################################################
# LOGGING AND SQLITE
################################################################################
# Database interaction
def accessDB(operation, query, vals):
    # TODO Sanitize input before feeding to cursor.execute substitution
    con = None
    try:
        dbPath = '/var/www/dvc-flask-app.com/logs.db'
        con = sqlite3.connect(dbPath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(query, vals)
        if operation == 'SELECT':
            return cur.fetchall()
        elif operation == 'INSERT':
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
