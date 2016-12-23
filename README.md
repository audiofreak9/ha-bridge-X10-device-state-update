# ha-bridge-X10-device-state-update
The Python script queries the ha-bridge for configured devices, and determines if they are X10 devices. It then gets the state of each X10 device from HEYU‘s state engine and updates the ha-bridge with that on/off and dim state as applicable.

<h3>Prerequisite components</h3>
* Linux box, preferably a Raspberry Pi, with <a href="https://www.python.org/">Python</a> installed
* Complete my <a href="http://coreyswrite.com/tips-tricks/amazon-echo-x10-home-control-updated/">Amazon Echo X10 Home Control tutorial</a>
* Set the directive “START_ENGINE AUTO” in the <a href="https://github.com/audiofreak9/HEYU-config-file-example/blob/master/x10config#L241">HEYU configuration file</a>

