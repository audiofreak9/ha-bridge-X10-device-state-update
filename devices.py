#!/usr/bin/python
import subprocess, requests, time, re, json
import paho.mqtt.client as mqtt  #import the mqtt client

#Set some Global variables
dimlevel = 0
devid = 0
mqttTopics = {}

#****************
#* UPDATE BELOW *
#****************

#HA_Bridge: IP, username, password
ha_ip = "[YOUR_ha_IP]"
ha_uname = "[YOUR_ha_USER]"
ha_upass = "[YOUR_ha_PASS]"
haveX10 = False #Set to True if you have X10 devices, heyu and CM11A

#mqtt: IP, username, password
mqtt_broker_ip = "[YOUR_mqtt_IP]"
mqtt_uname = "[YOUR_mqtt_USER]"
mqtt_upass = "[YOUR_mqtt_PASS]"
mqtt_topic = "Murn-Blinds/+"
havemqtt = False #Set to True if you have mqtt devices
mqtt100_0 = False #set to True if you have MK-Smarthouse blinds and 100 and 0 are both closed based on servo orientation

#****************
#* UPDATE ABOVE *
#****************

#makes mqtt connection
def on_connect(client, userdata, flags, rc):
        if rc==0:
                client.connected_flag=True #set flag
                print ("** mqtt: Connected OK")
        else:
                print("** mqtt: connection Returned code=",rc)

#update device in HA_Bridge
def dev_update(dimlevel):
        url = "http://%s/api/c/lights/%s/bridgeupdatestate" % (ha_ip, devid)
        if dimlevel != "":
                if dimlevel > 0:
                        dimlevelup = int((dimlevel*255)/100)
                        state = "true"
                else:
                        state = "false"
                payload = "{\"on\":%s" % state
                if state == "true":
                        payload = "%s, \"bri\":%s" % (payload, dimlevelup)
                payload = "%s}" % payload
                print ("** - Set to %s in HA-Bridge" % payload)
                r = requests.put(url, data=payload)

#mqtt message (calls dev_update) into dictionary
def on_message(client, userdata, message):
        topic = message.topic
        dimlevel = int(message.payload.decode("utf-8"))
        mqttTopics[topic] = dimlevel

#is_mqtt (calls on_message)
def is_mqtt(topic):
        client.subscribe(topic,1)
        client.on_message = on_message
        time.sleep(0.8)
        print ("** mqtt: Device states obtained successfully")
        client.unsubscribe(topic)

if havemqtt == True or haveX10 == True :
        #Get devices from HA-Bridge
        print (" ")
        print ("HA-Bridge: ********************************************************************")
        print ("HA-Bridge: Obtaining devices from %s" % (ha_ip))
        ha_url = "http://%s/api/devices" % ha_ip
        json_string = requests.get(ha_url, auth=(ha_uname, ha_upass)).json()
        print ("HA-Bridge: Devices obtained successfully")
        if havemqtt == True :
                print ("** mqtt: *************************************************************************")
                #Make mqtt connection
                mqtt.Client.connected_flag=False #create flag in class
                client = mqtt.Client('mqtt')             #create new instance 
                client.on_connect=on_connect  #bind call back function
                client.loop_start()
                print ("** mqtt: Connecting to broker %s" % mqtt_broker_ip)
                client.username_pw_set(mqtt_uname, mqtt_upass)
                client.connect(mqtt_broker_ip)      #connect to broker
                while not client.connected_flag: #wait in loop
                        print ("** mqtt: Connecting...")
                        time.sleep(1)
                is_mqtt(mqtt_topic)
                client.loop_stop()
                client.disconnect() # disconnect
                print ("** mqtt: Disconnected from broker")
                #Loop through devices and update mqtt devices
                for device in json_string:
                        if device['deviceType'] == "mqtt":
                                if device['targetDevice'].find("/") != -1 : #Check that the topic has a backslash 'Group/Device'
                                        print ("** mqtt: HA-Bridge Device ID %s is an mqtt device (%s)" % (device['id'], device['name']))
                                        devid = device['id']
                                        dimlevel = int(mqttTopics[device['targetDevice']])
                                        dev_update(dimlevel)
                                else:
                                        print ("** mqtt: HA-Bridge Device ID %s is an mqtt group not a topic (%s)" % (device['id'], device['name']))
                                        print ("** - Next")
                print ("HA-Bridge: mqtt Device update successful")
        if haveX10 == True :
                print ("** X10: **************************************************************************")
                #Get X10 data from CM11A
                print ("** X10: Getting device states from heyu / CM11A")
                heyuRegex = re.compile(r'[a-zA-Z]{1}\d{1,2}') #set heyuRegex to find Letter/Number houseunit
                (alllevel, err) = subprocess.Popen(["/usr/local/bin/heyu show dim"], stdout=subprocess.PIPE, shell=True).communicate()
                #Create a 16 x 16 X10Matrix, all set to 0 initially
                w, h = 16, 16;
                X10Matrix = [[0 for x in range(w)] for y in range(h)]
                for column in range(0,16):
                        getColumn = int(column+3) #Add three to skip the first 3 rows
                        thisRow = alllevel.split(b'\n')[getColumn].strip().split()
                        for row in range(0,16):
                                getRow = int(row+1)
                                if int(thisRow[getRow]) > 0: #Only update if > 0
                                        X10Matrix[column][row] = thisRow[getRow]
                print ("** X10: Device states obtained successfully")
                #Loop through the devices and update the x10 devices
                for device in json_string:
                        if device["onUrl"].find("heyu") != -1 : #Check if the 'heyu' command is present
                                HU = heyuRegex.search(device["onUrl"])
                                if HU:
                                        print ("** X10: HA-Bridge Device ID %s is an X10 device [%s] (%s)" % (device['id'], HU.group(), device['name']))
                                        #Find the Unit Number
                                        thisRowVal = int(re.sub('[a-zA-Z]',  '', HU.group())) - 1 #Subtract one for base 0 array
                                        #Find the ordinal value of the Housecode
                                        thisLetterVal = int(ord(re.sub('[0-9]',  '', HU.group()))) - 65 #Subtract sixtyfive to get 'A' = 0, 'B' = 1, etc...
                                        #Get the dimlevel from the X10Matrix
                                        dimlevel = int(X10Matrix[thisLetterVal][thisRowVal])
                                        devid = device['id']
                                        dev_update(dimlevel)
                                else:
                                        print ("** X10: HA-Bridge Device ID %s is an X10 command (%s)" % (device['id'], device['name']))
                                        print ("** - Next")
                print ("HA-Bridge: X10 Device update successful")
        #Loop through the devices and report remaining not updated
        print ("** OTHER: *************************************************************************")
        for device in json_string:
                if device["onUrl"].find("heyu") == -1 and device['deviceType'] != "mqtt":
                        print ("** %s: HA-Bridge Device ID %s not an updateable device (%s)" % (device['mapType'], device['id'], device['name']))
                        #print ("** - Next")
        print ("HA-Bridge: Update successfully completed")
        print (" ")
else:
        print (" ")
        print ("**********************************************************************************")
        print ("** Both 'haveX10' and' 'havemqtt' variables set to False - nothing to update!   **")
        print ("**********************************************************************************")
        print (" ")
