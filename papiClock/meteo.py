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

# Many thanks to InfoClimat: http://www.infoclimat.fr
# InfoClimat is a non profit association of weather enthusiasts making
# their weather prediction API freely available

import urllib2, urllib, json
import threading, time, datetime
import test

METEO_BASE_URL = "http://www.infoclimat.fr/public-api/gfs/json?_ll={lat:.6f},{lon:.6f}&_auth=AhhRRlIsAyFVeFZhA3UHLlM7BDFaLAIlAn4DYFs%2BUy5SOQVkD29RN14wUy4BLlZgUXxQMwA7AjJROlIqAXMEZQJoUT1SOQNkVTpWMwMsByxTfQRlWnoCJQJpA2ZbKFMyUjMFaQ9yUTFeNFMzAS9WYFFjUDIAIAIlUTNSMAFsBGYCYlE1UjUDZVU%2FVjMDLAcsU2UEbVpiAmkCYANiWz5TOVI5BWgPOVE3XmVTMwEvVmRRa1A3ADYCPVE1UjQBZQR4An5RTFJCA3xVelZ2A2YHdVN9BDFaOwJu&_c=3f9569aaf189f4574d6c65e2f9ae66f0"

class InfoClimat(object):
    def __init__(self, latitude, longitude):
        self.url = METEO_BASE_URL.format(lat=latitude, lon=longitude)
    
class Meteo(object):
    def __init__(self, latitude, longitude):
        self.info_climat = InfoClimat(latitude, longitude)
        self.result_info_climat = None
        self.data_available = False
        self.run_number = 0
        self.previous_run_number = 0
        self.data = {}
        
    def getInfoWorker(self, url):
        #result = urllib2.urlopen(self.info_climat.url).read()
        time.sleep(1)
        self.result_info_climat = test.METEO_TEST_RESULT
        print("%s: Meteo.getInfoWorker: Got result" % __file__)
        self.parseInfo()
        self.data_available = True

    def getInfo(self):
        t = threading.Thread(target=self.getInfoWorker, args=(self.info_climat.url,))
        t.start()
        
    def parseInfo(self):
        http_rc = self.result_info_climat.get("request_state", 0)
        if http_rc == 200:
            msg_rc = self.result_info_climat.get("message", "KO")
            if msg_rc == "OK":
                print("%s: Meteo.parseInfo: request OK" % __file__)
            else:
                print("%s: Meteo.parseInfo: message error %s" % (__file__, message_rc))
                return
        else:
            print("%s: Meteo.parseInfo: request error %d" % (__file__, http_rc))
            return;
        for k, v in self.result_info_climat.iteritems():
            try:
                if k == "request_state":
                    pass
                elif k == "message":
                    pass
                elif k == "request_key":
                    pass
                elif k == "source":
                    pass
                elif k == "model_run":
                    self.previous_run_number = self.run_number
                    self.run_number = int(v)
                else:
                    ts = datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S")
                    self.data[ts] = self.parseItem(ts, v)
            except ValueError:
                print("%s: Meteo.parseInfo: invalid value %s at key %s" % (__file__, v, k))
                pass
            except Exception as e:
                print("%s: Meteo.parseInfo: Exception %s at key %s" % (__file__, str(e), k))
                pass
        
    def parseItem(self, ts, info):
        meteo_info = {}
        for k, v in info.iteritems():
            try:
                if k == "pression":
                    meteo_info["pression"] = v["niveau_de_la_mer"] / 100.0
                elif k == "temperature":
                    meteo_info["temperature"] = round(v["2m"] -273.0, 1)
                elif k == "pluie":
                    meteo_info["pluie"] = v
                elif k == "vent_moyen":
                    meteo_info["vent_moyen"] = v["10m"]
                elif k == "vent_rafales":
                    meteo_info["vent_rafales"] = v["10m"]
                elif k == "vent_direction":
                    meteo_info["vent_direction"] = int(v["10m"]) % 360
                elif k == "risque_neige":
                    meteo_info["risque_neige"] = (v == "oui")
            except Exception as e:
                print("%s: Meteo.parseItem: Date %s Exception %s at key %s" % (__file__, ts, str(e), k))
                pass
        return meteo_info
                
    def getMeteo(self, now):
        date_keys = self.data.keys()
        date_keys.sort()
        meteo_dict = {}
        meteo_dict["items"] = ["hour", "pres", "temp", "wind"]
        meteo_dict["hour"] = []
        meteo_dict["pres"] = []
        meteo_dict["temp"] = []
        meteo_dict["wind"] = []
        for dk in date_keys:
            if dk > now - datetime.timedelta(hours=3):
                if len(meteo_dict["hour"]) == 0 and self.previous_run_number != self.run_number:
                    meteo_dict["hour"].append(dk.strftime("%H:%M*"))
                else:
                    meteo_dict["hour"].append(dk.strftime("%H:%M "))                    
                pres = self.data[dk].get("pression", 0)
                meteo_dict["pres"].append("%.1f" % pres)
                temp = self.data[dk].get("temperature", 0)
                pluie = self.data[dk].get("pluie", 0)
                if pluie >= 100:
                    pluie = 99
                meteo_dict["temp"].append("%+2.0f %2.0f" % (temp, round(pluie, 0)))
                vent_moy = self.data[dk].get("vent_moyen", 0)
                if vent_moy >= 100:
                    vent_moy = 99
                vent_dir = self.data[dk].get("vent_direction", 0)
                meteo_dict["wind"].append("%2.0f %03d" % (vent_moy, vent_dir))
                if len(meteo_dict["hour"]) == 4:
                    break
        return meteo_dict
                
