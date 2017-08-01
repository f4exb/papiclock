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

import sys, time, datetime
import papiClock

METEO_LATITUDE = 43.5764327
METEO_LONGITUDE = 7.1042904

def main(argv):
    meteo = papiClock.Meteo(METEO_LATITUDE, METEO_LONGITUDE)
    meteo.getInfo()
    while meteo.data_available is False:
        time.sleep(1)
        print("wait")
    now = datetime.datetime(2017, 8, 1, 10, 59)
    meteo_dict = meteo.getMeteo(now)
    lines = []
    for i in range(len(meteo_dict) - 1):
        lines.append("|")
    for ix in range(4):
        for iy,it in enumerate(meteo_dict["items"]):
            lines[iy] += (meteo_dict[it][ix] + "|")
    for line in lines:
        print(line)

# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
