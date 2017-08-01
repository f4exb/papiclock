#!/usr/bin/env python

# Copyright 2017 Edouard Griffiths, F4EXB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.  See the License for the specific language
# governing permissions and limitations under the License.

import re
import subprocess
import json, requests
import logger

# Create googlekey.py inside papiClock package with a single line:
# KEY=<YOUR_API_KEY>
import googlekey

cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
regexps = [
    re.compile(r"^ESSID:\"(?P<essid>.*)\"$"),
    re.compile(r"^Protocol:(?P<protocol>.+)$"),
    re.compile(r"^Mode:(?P<mode>.+)$"),
    re.compile(r"^Frequency:(?P<frequency>[\d.]+) (?P<frequency_units>.+) \(Channel (?P<channel>\d+)\)$"),
    re.compile(r"^Encryption key:(?P<encryption>.+)$"),
    re.compile(r"^Quality=(?P<signal_quality>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<signal_level_dBm>.+) d.+$"),
    re.compile(r"^Signal level=(?P<signal_quality>\d+)/(?P<signal_total>\d+).*$"),
]

# Runs the comnmand to scan the list of networks.
# Must run as super user.
# Does not specify a particular device, so will scan all network devices.
def scan(interface='wlan0'):
    cmd = ["iwlist", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    scantext = proc.stdout.read().decode('utf-8')
    return scantext

# Parses the response from the command "iwlist scan"
def parse(content):
    cells = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
        else:
            for expression in regexps:
                result = expression.search(line)
                if result is not None:
                    cells[-1].update(result.groupdict())
    return cells

class WifiLocate:
    def __init__(self, interface='wlan0'):
        zlog = logger.getLogger()
        try:
            scantext = scan(interface)
            self.cells = parse(scantext)
            zlog.logger.info(self.cells)
            self.lat = 0
            self.lon = 0
            self.radius = None
        except Exception as e:
            zlog.logger.error("Exception %s in WifiLocate constructor" % str(e))
        
    def locate(self):
        zlog = logger.getLogger()
        request = {
            "considerIp": "false",
            "wifiAccessPoints": []
        }
        for cell in self.cells:
            try:
                ap = {"signalToNoiseRatio": 0}
                ap["macAddress"] =  cell["mac"]
                ap["signalStrength"] = int(cell["signal_level_dBm"])
                request["wifiAccessPoints"].append(ap)
            except Exception as e:
                zlog.logger.error("Exception %s for cell %s" % (str(e), str(cell)))
        try:
            googleurl = "https://www.googleapis.com/geolocation/v1/geolocate?key=%s" % googlekey.KEY
            r = requests.post(googleurl, json=request)
            if r.status_code == 200:
                response = r.json()
                self.radius = response["accuracy"]
                self.lat = response["location"]["lat"]
                self.lon = response["location"]["lng"]
                zlog.logger.info("Google Maps replied: lat=%f, lon=%f, radius=%f" % (self.lat, self.lon, self.radius))
            else:
                zlog.logger.error("Google Maps API returned code %d" % r.status_code)
        except Exception as e:
            zlog.logger.error("Exception %s occured while processing Google Maps API" % str(e))
