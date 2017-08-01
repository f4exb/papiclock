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

import sys
import argparse
import papiClock

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-I", "--interface", help="wireless network interface", default="wlan0")
    parser.add_argument("-L", "--latitude", help="latitude of point of interest", type=float)
    parser.add_argument("-l", "--longitude", help="longitude of point of interest", type=float)
    args = parser.parse_args()    

    if args.latitude and args.longitude:
	print("ll=%f,%f" %(args.latitude, args.longitude))
    else:
        geoloc = papiClock.WifiLocate()
        if geoloc.scan(interface=args.interface):
            geoloc.locate()
        if geoloc.radius:
            print("ll=%f,%f" % (geoloc.lat, geoloc.lon))
        else:
            print("cannot geolocate")

# main
if "__main__" == __name__:
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass

