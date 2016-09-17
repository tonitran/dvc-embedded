#!/usr/local/bin/bash

# Set up GPIO 4 and set to input
echo "4" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio4/direction

### DIRECTIONS ###
Place this file in /usr/local/bin.
Give it execution permission (chmod +x).
Edit the sudoers file with visudo and allow user 'www-data' permission to run this script.
Set up a cron job that will run this script on reboot.
