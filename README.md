Embedded Door Sensor
===

This is the script running on the Raspberry Pi that allows it to poll the state of the door, as well as expose a REST endpoint for polling. Feel free to add any features that you want (after vigorous testing, of course)!

SSH
---
You can SSH into the Pi at the assigned address with your public key on the server. Ask the project admin to add your credentials.

Dependencies
---
The app runs on an RPI2 model B and uses [FLASK](http://flask.pocoo.org/) for the REST calls. Install python-dev before running `pip install wiringpi2`.

It also uses the [WiringPi](http://raspi.tv/how-to-install-wiringpi2-for-python-on-the-raspberry-pi) library for GPIO pin reading.

Running
---
The sensor-init script runs automatically on startup via the /etc/init.d/ scripts, which will do the following:

    cd /home/pi/dvc-door-sensor
    export FLASK_APP=sensor.py
    flask run --host=0.0.0.0

The endpoint will then be available at dvc-raspberrypi.ucsd.edu:5000/door.
The output can be found at /var/log/rc.local.log.

Killing
---
To kill the process, just run (if on Linux):
kill $(pidof python)

Assigned by the UCSD Hostmaster
---
- IP=132.239.214.30
- Hostname=dvc-raspberrypi.ucsd.edu
- Gateway=132.239.214.1
- Net Mask=255.255.255.192

Future Feature Ideas
---
- Saving a log of the most active and inactive times and exposing that via a REST call.
- Landing page with features for requesting access, emailing, and more.
- DDOS protection.
- IR sensor
- Shutdown button
- If upgrading sd card, install debian netinst (headless) instead.
- Got any more ideas? Add them!
