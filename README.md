# ha-bridge-X10-device-state-update
The Python script queries the ha-bridge for configured devices, and determines if they are X10 devices. It then gets the state of each X10 device from HEYU‘s state engine and updates the ha-bridge with that on/off and dim state as applicable.

<h3>Prerequisite components</h3>

* Linux box, preferably a Raspberry Pi, with <a href="https://www.python.org/">Python</a> installed

* Complete my <a href="http://coreyswrite.com/tips-tricks/amazon-echo-x10-home-control-updated/">Amazon Echo X10 Home Control tutorial</a>

* Set the directive “START_ENGINE AUTO” in the <a href="https://github.com/audiofreak9/HEYU-config-file-example/blob/master/x10config#L241">HEYU configuration file</a>

<h3>Install</h3>

* Copy the devices.py file to your "habridge" directory on the Raspberry Pi.

* Replace the two instances of [YOUR_RPI_IP] in the code with your Rasperry Pi's IP.

* Replace the [YOUR_HOUSECODE] in the code with your X10 Housecode, for me it would be M.

<h3>Usage</h3>

* From the command line: `$ python devices.py`

* In a cronjob `*/10 * * * * python /home/pi/habridge/devices.py > /dev/null 2>&1`
