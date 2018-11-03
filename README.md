# ha-bridge-device-state-update
The Python script queries the ha-bridge for configured devices, and determines if they are mqtt or X10 devices. It then gets the state of each X10 device from HEYU‘s state engine and stored mqtt message states from the broker and updates the ha-bridge with that on/off and dim state as applicable.

<h3>Prerequisite components</h3>

* Linux box, preferably a Raspberry Pi, with <a href="https://www.python.org/">Python</a> installed

* Complete my <a href="http://coreyswrite.com/tips-tricks/amazon-echo-x10-home-control-updated/">Amazon Echo X10 Home Control tutorial</a>

* Set the directive “START_ENGINE AUTO” in the <a href="https://github.com/audiofreak9/HEYU-config-file-example/blob/master/x10config#L241">HEYU configuration file</a>

<h3>Install</h3>

* Copy the devices.py file to your "habridge" directory on the Raspberry Pi.

* Make the script executable: `$ sudo chmod +x devices.py`

* Replace the [YOUR_IP] variable in the code with your Rasperry Pi's IP.

* Replace the [YOUR_USER] and [YOUR_PASS] in the code with your HA Bridge username and password.  NOTE: My HA-Bridge and mqtt broker use the same IP, username and password, so your milage may vary.

<h3>Usage</h3>

* From the command line: `$ python devices.py`

* In a cronjob `*/10 * * * * python /home/pi/habridge/devices.py > /dev/null 2>&1`
