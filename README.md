- [Master ![Build Status](https://travis-ci.org/tonitran/dvc-embedded.svg?branch=master)](https://travis-ci.org/tonitran/dvc-embedded)
- [Develop ![Build Status](https://travis-ci.org/tonitran/dvc-embedded.svg?branch=develop)](https://travis-ci.org/tonitran/dvc-embedded)

Embedded Door Sensor
===
This is the script running on the Raspberry Pi that allows it to poll the state of the door, as well as expose a REST endpoint for polling. Feel free to add any features that you want (after vigorous testing, of course)!

How to Contribute
---
- Follow the [Git branching process](http://nvie.com/posts/a-successful-git-branching-model/).
Always make feature branches off of `develop`. Submit a pull request against develop when ready.
- Test thoroughly on develop before merging into `master`. Master is the production branch and should **always be stable**.
- Deploy on your own Raspberry Pi running local first. If all is well, push to master and then update said code on the production device.

SSH
---
Password verification is disabled for security purposes. You can SSH into the Pi at the assigned address with your public key on the server. Ask the project administrators to add your credentials. An admin simply needs to append your public key to the Pi's authorized hosts file.

Development
---
It is best to simulate the production environment as closely as possible by having a Pi to test with. Note, however, that this can also all be done without a Raspberry Pi, by setting the environment within `runConfigs.py`. See the Deployment section on setting up virtual hosts.

1. Modify runConfigs.py to change endpoints.
2. Use Postman to test manually. You can import the Postman dump included.

Testing
---
Add tests to `test-script.py` so Travis can run them.

Deployment
---
1. Apache Setup
  2. Set up virtual hosts (see below), one that will be accessed internally at `www.dvc-flask-app.com`. All the files found in this folder will be moved to `/var/www/dvc-flask-app.com`. You may create a soft link and place it on your desktop for easier access if necessary.
  3. Enable mod_proxy, mod_http_proxy, mod_wsgi, and mod_mpm_prefork (disable mpm_events first).
4. Ownership and Permissions
  1. chmod -R 755 ${app directory}. This will allow the Apache2 system user to make changes to the database file.
  2. chown -R www-data:www-data ${app directory}. Do the same without the recursive flag to chown the parent directory. This is needed for the same reasons as above.

Virtual Host Configuration
---
```xml
# /etc/apache2/sites-available/dvc-flask-app.com.conf
<VirtualHost *:80>
	...
    WSGIDaemonProcess dvc-flask-app user=www-data group=www-data threads=5
    WSGIScriptAlias / /var/www/dvc-flask-app.com/dvc-embedded.wsgi
    ...
	DocumentRoot /var/www/dvc-flask-app.com
    ....
    <Directory /var/www/dvc-flask-app.com>
        WSGIScriptReloading On
        WSGIProcessGroup dvc-flask-app
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

Assigned by the UCSD Hostmaster
---
- IP=132.239.214.30
- Hostname=dvc-raspberrypi.ucsd.edu
- Gateway=132.239.214.1
- Net Mask=255.255.255.192

Summary Workflow
---
1. Make feature branch off of develop.
2. Push up remote feature branch and make pull request.
3. Review code and push updated changes if needed.
4. Merge into develop (with --no-ff option).
5. After many features have been merged into develop, creating a release branch from it. Give it a version number. v{MAJOR}.{MINOR}.{HOTFIX}.
6. "Bump" the release branch by making any last minute changes in preparation for production. This may include updating the README, updating environment variables to point to production endpoints, etc.
7. Pull in the release branch's changes from both master and develop. Be sure to tag the master branch with the new version. The release branch may now be deleted.
8. On the production device, perform the fast-forward pull on the master branch. Make sure everything works. If not, it may be necessary to make a hotfix branch.

Future Feature Ideas
---
- DDOS protection.
- IR sensor
- Shutdown button
- If upgrading sd card, install debian netinst (headless) instead.
- Got any more ideas? Add them!
