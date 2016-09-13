#!/usr/bin/python3.5

import sqlite3

print("Test script running! Define your own tests within test-script.py.")


# Save door state to log file.
def logDoorState(jsonValue, year, month, day, hour, minute):
    con = None
    try:
        con = sqlite3.connect('logs.db')
        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        print("SQLite version: %s" % data)
    except lite.Error as e:
        print("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if con:
            con.close()

logDoorState(1,1,1,1,1,1)
