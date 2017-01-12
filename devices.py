#!/usr/bin/env python
import urllib2, subprocess, requests, time
timestamp = time.strftime("Time: %H:%M, Date: %Y%m%d, ")
print timestamp
for device in requests.get('http://localhost/api/devices').json():
    if device['onUrl'].find('heyu') != -1:
        url = "http://localhost/api/c/lights/%s/bridgeupdatestate" % device['id']
        chtxt = device['onUrl'].replace("python", "").replace(",", "").replace(":", "").replace("\"", "").replace("item", "").replace("typenull", "").replace("typecmdDevice", "").replace("[{", "").replace("}]", "").replace("fon", "dimlevel").replace("on","dimlevel")
        if chtxt.find('dimlevel') != -1:
            proc = subprocess.Popen([chtxt], stdout=subprocess.PIPE, shell=True)
            (dimlevel, err) = proc.communicate()
            dimlevel = int(dimlevel)
            if dimlevel > 0:
                dimlevel = ((dimlevel*255)/100)
                state = "true"
            else:
                state = "false"
            payload = "{\"on\":%s" % state
            if state == "true":
                payload = "%s, \"bri\":%s" % (payload, dimlevel)
            payload = "%s}" % payload
            print "Device ID %s set to %s (%s)" % (device['id'], payload, device['name'])
            r = requests.put(url, data=payload)
        else:
            print "Device ID %s is an X10 command (%s)" % (device['id'], device['name'])
    else:
        print "Device ID %s not an X10 device (%s) - [%s]" % (device['id'], device['name'], device['mapType'])
