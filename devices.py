#!/usr/bin/env python
import urllib2, subprocess, requests, time
timestamp = time.strftime("Time: %H:%M, Date: %Y%m%d, ")
print timestamp
for device in requests.get('http://localhost/api/devices').json():
    if device['offUrl'].find('heyu') != -1:
        url = "http://localhost/api/c/lights/%s/bridgeupdatestate" % device['id']
        chtxt = device['offUrl'].replace("foff", "dimlevel").replace("off","dimlevel")
        if chtxt.find('dimlevel') != -1:
            proc = subprocess.Popen([chtxt], stdout=subprocess.PIPE, shell=True)
            (dimlevel, err) = proc.communicate()
            dimlevel = int(dimlevel)
            if dimlevel > 0:
                dimlevel = ((dimlevel*255)/100)
                state = "true"
            else:
                state = "false"
            print "Device ID %s set to %s at dim level %s (%s)" % (device['id'], state, dimlevel, device['name'])
            r = requests.put(url, json={"on":state, "bri":dimlevel})
        else:
            print "Device ID %s is an X10 command (%s)" % (device['id'], device['name'])
    else:
        print "Device ID %s not an X10 device (%s)" % (device['id'], device['name'])
