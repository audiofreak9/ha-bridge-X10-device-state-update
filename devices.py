#!/usr/bin/python
import subprocess, requests, time, re, json
heyuRegex = re.compile(r'[a-zA-Z]{1}\d{1,2}')
(alllevel, err) = subprocess.Popen(["/usr/local/bin/heyu show dim"], stdout=subprocess.PIPE, shell=True).communicate()
Mlevelarray = alllevel.split('\n')[15].strip().split()
json_string = requests.get('http://[YOUR_RPI_IP]/api/devices', auth=('[YOUR_HABRIDGE_USERNAME]', '[YOUR_HABRIDGE_PASSWORD]')).json()
for device in json_string:
        if device["onUrl"].find("heyu") != -1 :
                HU = heyuRegex.search(device["onUrl"])
                if HU:
                        url = "http://[YOUR_RPI_IP]/api/c/lights/%s/bridgeupdatestate" % device['id']
                        dimlevel = int(Mlevelarray[int(HU.group().replace("[YOUR_HOUSECODE]", ""))])
                        if dimlevel > 0:
                                dimlevel = ((dimlevel*255)/100)
                                state = "true"
                        else:
                                state = "false"
                        payload = "{\"on\":%s" % state
                        if state == "true":
                                payload = "%s, \"bri\":%s" % (payload, dimlevel)
                        payload = "%s}" % payload
                        print "Device ID %s, HU %s set to %s (%s)" % (device['id'], HU.group(), payload, device['name'])
                        r = requests.put(url, data=payload)
                else:
                        print "Device ID %s is an X10 command (%s)" % (device['id'], device['name'])
        else:
                print "Device ID %s not an X10 device (%s) - [%s]" % (device['id'], device['name'], device['mapType'])
