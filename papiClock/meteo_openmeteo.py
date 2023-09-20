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

# Many thanks to Open-Meteo: https://open-meteo.com/
# Open-Meteo offers free access to its APIs for non-commercial use,
# making it convenient for individuals and developers to explore
# and integrate weather data into their projects.

import urllib.request, json
import threading, time, datetime
import test
import papiClock.logger as logger

RUN_NUMBER = 0
METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast?latitude={lat:.6f}&longitude={lon:.6f}&hourly=temperature_2m,relativehumidity_2m,precipitation,snowfall,pressure_msl,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,windspeed_10m,winddirection_10m,windgusts_10m,soil_temperature_0cm,freezinglevel_height,temperature_850hPa,temperature_500hPa"

class OpenMeteo(object):
    def __init__(self, latitude, longitude):
        self.url = METEO_BASE_URL.format(lat=latitude, lon=longitude)

class Meteo(object):
    def __init__(self, latitude, longitude, nb_meteo_items=4):
        self.meteo_info = OpenMeteo(latitude, longitude)
        self.nb_meteo_items = nb_meteo_items
        self.result_meteo_info = None
        self.result_available = False
        self.data_available = False
        self.run_number = 0
        self.previous_run_number = 0
        self.data = {}

    def getInfoWorker(self, url):
        zlog = logger.getLogger()
        r = urllib.request.urlopen(url)
        if r.getcode() == 200:
            result = r.read()
            self.result_meteo_orig = json.loads(result)
            #time.sleep(1)
            #self.result_meteo_info = test.METEO_TEST_RESULT
            zlog.logger.info("Got result")
            self.parseInfo()
            self.data_available = True
        else:
            zlog.logger.error("Open-Meteo returned %d" % r.getcode())
            self.data_available = False

    def getInfo(self):
        t = threading.Thread(target=self.getInfoWorker, args=(self.meteo_info.url,))
        t.start()

    def parseInfo(self):
        global RUN_NUMBER
        if RUN_NUMBER < 100:
            RUN_NUMBER += 1
        else:
            RUN_NUMBER = 1
        self.convertInfo()
        self.parseInfoLegacy()

    def convertInfo(self):
        self.result_meteo_info = {}
        self.result_meteo_info["request_state"] = 200
        self.result_meteo_info["request_key"] = "fd543c77e33d6c8a5e218e948a19e487"
        self.result_meteo_info["message"] = "OK"
        self.result_meteo_info["model_run"] = "%02d" % RUN_NUMBER
        self.result_meteo_info["source"] =  "internal:GFS:1"
        time_line = self.result_meteo_orig["hourly"]["time"]
        for time_index, time_stanp in enumerate(time_line):
            dt = datetime.datetime.strptime(time_stanp, "%Y-%m-%dT%H:%M")
            report_item = {}
            self.result_meteo_info[dt.strftime("%Y-%m-%d %H:%M:%S")] = report_item
            report_item["temperature"] = {
                "2m": self.result_meteo_orig["hourly"]["temperature_2m"][time_index] + 273,
                "sol": self.result_meteo_orig["hourly"]["soil_temperature_0cm"][time_index] +273,
                "500hPa": self.result_meteo_orig["hourly"]["temperature_500hPa"][time_index] +273,
                "850hPa": self.result_meteo_orig["hourly"]["temperature_850hPa"][time_index] +273
            }
            report_item["pression"] = {
                "niveau_de_la_mer": self.result_meteo_orig["hourly"]["pressure_msl"][time_index]*100
            }
            report_item["pluie"] = round(self.result_meteo_orig["hourly"]["precipitation"][time_index])
            report_item["pluie_convective"] = 0
            report_item["humidite"] = {
                "2m": self.result_meteo_orig["hourly"]["relativehumidity_2m"][time_index]
            }
            report_item["vent_moyen"] = {
                "10m": self.result_meteo_orig["hourly"]["windspeed_10m"][time_index]
            }
            report_item["vent_rafales"] = {
                "10m": self.result_meteo_orig["hourly"]["windgusts_10m"][time_index]
            }
            report_item["vent_direction"] = {
                "10m": self.result_meteo_orig["hourly"]["winddirection_10m"][time_index]
            }
            report_item["iso_zero"] = round(self.result_meteo_orig["hourly"]["freezinglevel_height"][time_index])
            report_item["risque_neige"] = "non" if self.result_meteo_orig["hourly"]["snowfall"][time_index] == 0 else "oui"
            report_item["cape"] = 0
            report_item["nebulosite"] = {
                "haute": self.result_meteo_orig["hourly"]["cloudcover_high"][time_index],
                "moyenne": self.result_meteo_orig["hourly"]["cloudcover_mid"][time_index],
                "basse": self.result_meteo_orig["hourly"]["cloudcover_low"][time_index],
                "totale": self.result_meteo_orig["hourly"]["cloudcover"][time_index]
            }

    def parseInfoLegacy(self):
        zlog = logger.getLogger()
        self.result_available = False
        http_rc = self.result_meteo_info.get("request_state", 0)
        if http_rc == 200:
            msg_rc = self.result_meteo_info.get("message", "KO")
            if msg_rc == "OK":
                zlog.logger.info("request OK")
            else:
                zlog.logger.error("message error %s" % msg_rc)
                return
        else:
            zlog.logger.error("request error %d" % http_rc)
            return
        self.result_available = True
        for k, v in self.result_meteo_info.items():
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
                    zlog.logger.info("Run number %d", self.run_number)
                else:
                    ts = datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S")
                    self.data[ts] = self.parseItem(ts, v)
            except ValueError:
                zlog.logger.error("invalid value %s at key %s" % (v, k))
                pass
            except Exception as e:
                zlog.logger.error("Exception %s at key %s" % (str(e), k))
                pass

    def parseItem(self, ts, info):
        zlog = logger.getLogger()
        meteo_info = {}
        for k, v in info.items():
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
                elif k == "humidite":
                     meteo_info["humidite"] = v["2m"]
            except Exception as e:
                zlog.logger.error("Date %s Exception %s at key %s" % (ts, str(e), k))
                pass
        return meteo_info

    def getMeteo(self, now):
        date_keys = list(self.data.keys())
        date_keys.sort()
        meteo_dict = {}
        meteo_dict["items"] = ["hour", "pres", "temp", "wind", "gust"]
        meteo_dict["hour"] = []
        meteo_dict["pres"] = []
        meteo_dict["temp"] = []
        meteo_dict["wind"] = []
        meteo_dict["gust"] = []
        date_count = -1
        for dk in date_keys:
            if dk > now - datetime.timedelta(hours=1):
                date_count += 1
                if date_count % 3 != 0:
                    continue
                if len(meteo_dict["hour"]) == 0 and self.previous_run_number != self.run_number:
                    meteo_dict["hour"].append(dk.strftime("%H:%M*"))
                else:
                    meteo_dict["hour"].append(dk.strftime("%H:%M "))
                pres = self.data[dk].get("pression", 0)
                meteo_dict["pres"].append("%.1f" % pres)
                temp = self.data[dk].get("temperature", 0)
                pluie = self.data[dk].get("pluie", 0)
                if pluie >= 100:
                    meteo_dict["temp"].append("%+2.0f%3.0f" % (temp, round(pluie, 0)))
                else:
                    meteo_dict["temp"].append("%+2.0f %2.0f" % (temp, round(pluie, 0)))
                vent_moy = self.data[dk].get("vent_moyen", 0)
                vent_dir = self.data[dk].get("vent_direction", 0)
                if vent_moy >= 100:
                    meteo_dict["wind"].append("%3.0f%03d" % (vent_moy, vent_dir))
                else:
                    meteo_dict["wind"].append("%2.0f %03d" % (vent_moy, vent_dir))
                vent_raf = self.data[dk].get("vent_rafales", 0)
                neige_char = "*" if self.data[dk].get("risque_neige", False) else " "
                humidite = self.data[dk].get("humidite", 0)
                if vent_raf >= 100:
                    meteo_dict["gust"].append("%3.0f%s%2.0f" % (vent_raf, neige_char, round(humidite, 0)))
                else:
                    meteo_dict["gust"].append("%2.0f %s%2.0f" % (vent_raf, neige_char, round(humidite, 0)))
                if len(meteo_dict["hour"]) == self.nb_meteo_items:
                    break
        return meteo_dict

