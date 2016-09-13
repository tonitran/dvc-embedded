- [Master ![Build Status](https://travis-ci.org/tonitran/dvc-embedded.svg?branch=master)](https://travis-ci.org/tonitran/dvc-embedded)
- [Develop ![Build Status](https://travis-ci.org/tonitran/dvc-embedded.svg?branch=develop)](https://travis-ci.org/tonitran/dvc-embedded)

Embedded Door Sensor
===
This is the script running on the Raspberry Pi that allows it to poll the state of the door, as well as expose a REST endpoint for polling. Feel free to add any features that you want (after vigorous testing, of course)!

How to Contribute
---
Follow the [Git branching process](http://nvie.com/posts/a-successful-git-branching-model/).
Always make feature branches off of `develop`. Submit a pull request against develop when ready.

Test thoroughly on develop before merging into `master`. Master is the production branch and should **always be stable**.

SSH
---
Password verification is disabled for security purposes. You can SSH into the Pi at the assigned address with your public key on the server. Ask the project administrators to add your credentials. An admin simply needs to append your public key to the Pi's authorized hosts file.

Dependencies
---
The app runs on an RPI2 model B and uses several services. You can install most of them with pip.
- [FLASK](http://flask.pocoo.org/) for the REST calls.
- [WiringPi](http://raspi.tv/how-to-install-wiringpi2-for-python-on-the-raspberry-pi) library for GPIO pin reading.
- Twisted for multithreading.

Running
---
The initialization script is added to /etc/rc.local so that it runs on bootup. In the future, I would like to make a proper init script that can be started with the standard init services.

To run it manually, you must type the following:
```
cd $(directory of dvc-embedded)
export FLASK_APP=sensor.py
flask run --host=0.0.0.0
```

The endpoint will then be available at dvc-raspberrypi.ucsd.edu:5000/door, if this code is running on the production server. Else, it will be running on localhost, or whatever virtual host you set.

The output can be found at /var/log/rc.local.log.

Stopping
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
