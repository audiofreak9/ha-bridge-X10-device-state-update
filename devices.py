#!/usr/bin/python
import subprocess, requests, time, re, json
import paho.mqtt.client as mqtt  #import the client

dimlevel = 0
ha_ip = "[YOUR_IP]"
uname = "[YOUR_USER]"
upass = "[YOUR_PASS]"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print " * Connected OK"
    else:
        print("Bad connection Returned code=",rc)

def dev_update(dimlevel, devid):
        url = "http://%s/api/c/lights/%s/bridgeupdatestate" % (ha_ip, device['id'])
        if dimlevel != "":
                if dimlevel > 0:
                        dimlevelup = ((dimlevel*255)/100)
                        state = "true"
                else:
                        state = "false"
                payload = "{\"on\":%s" % state
                if state == "true":
                        payload = "%s, \"bri\":%s" % (payload, dimlevelup)
                payload = "%s}" % payload
                print " - Set to %s" % payload
                r = requests.put(url, data=payload)

def on_message(client, userdata, message):
        dimlevel = int(message.payload.decode("utf-8"))
        if dimlevel == 100:
                dimlevel = 0
        dev_update(dimlevel, 'mqtt')

def mqtt_update(topic):
        client.loop_start()
        client.subscribe(topic,1)
        client.on_message = on_message
        time.sleep(0.8)
        client.loop_stop()    #Stop loop 

#Get devices from HA-Bridge
print "Getting HA-Bridge devices"
ha_url = "http://%s/api/devices" % ha_ip
json_string = requests.get(ha_url, auth=(uname, upass)).json()

#Make mqtt connection
mqtt.Client.connected_flag=False #create flag in class
broker = ha_ip
client = mqtt.Client('mqtt')             #create new instance 
client.on_connect=on_connect  #bind call back function
client.loop_start()
print " * Connecting to mqtt broker %s" % broker
client.username_pw_set(uname, upass)
client.connect(broker)      #connect to broker
while not client.connected_flag: #wait in loop
    print " * Connecting..."
    time.sleep(1)
client.loop_stop()

#Loop through devices and update mqtt devices
for device in json_string:
        if device['deviceType'] == "mqtt":
                if device['targetDevice'].find("/") != -1 : #Check for group/topic mqtt structure
                        print "Device ID %s is an mqtt device (%s)" % (device['id'], device['name'])
                        mqtt_update(device['targetDevice'])
                else:
                        print "Device ID %s is an mqtt group not a topic (%s)" % (device['id'], device['name'])
                        print " - Next device"
client.disconnect() # disconnect
print " * Disconnected from mqtt broker %s" % broker

#Get X10 data from CM11A
print " * Getting X-10 device states from CM11A"
heyuRegex = re.compile(r'[a-zA-Z]{1}\d{1,2}')
(alllevel, err) = subprocess.Popen(["/usr/local/bin/heyu show dim"], stdout=subprocess.PIPE, shell=True).communicate()
print alllevel
Mlevelarray = alllevel.split('\n')[15].strip().split()

#Loop through the devices and update the x10 devices
for device in json_string:
        if device["onUrl"].find("heyu") != -1 :
                HU = heyuRegex.search(device["onUrl"])
                if HU:
                        print "Device ID %s is an X10 device (%s)" % (device['id'], device['name'])
                        dimlevel = int(Mlevelarray[int(re.sub('[a-zA-Z]',  '', HU.group()))])
                        devid = "HU %s" % HU.group()
                        dev_update(dimlevel, devid)
                else:
                        print "Device ID %s is an X10 command (%s)" % (device['id'], device['name'])
        elif device['deviceType'] != "mqtt":
                print "Device ID %s not an updateable device (%s) - [%s]" % (device['id'], device['name'], device['mapType'])
                print " - Next device"
