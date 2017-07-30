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
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import papiClock

METEO_LATITUDE = 43.5764327
METEO_LONGITUDE = 7.1042904

#CLOCK_FONT_FILE = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
CLOCK_FONT_FILE = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

#DATE_FONT_FILE  = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
DATE_FONT_FILE = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

#METEO_FONT_FILE  = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
METEO_FONT_FILE  = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    
CLOCK_WEEKDAYS = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]
CLOCK_MONTHS   = ["JAN", "FEV", "MAR", "AVR", "MAI", "JUN", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

WHITE = 1
BLACK = 0

def format_time(now):
    return '{h:02d}:{m:02d}:{s:02d}'.format(h=now.hour, m=now.minute, s=now.second)

def format_date(now):
    return '{dow} {d:02d} {moy}'.format(dow=CLOCK_WEEKDAYS[now.weekday()], d=now.day, moy=CLOCK_MONTHS[now.month - 1])

def meteo_test():
    meteo_dict = {}
    meteo_dict["items"] = ["hour", "pres", "temp", "wind", "gust"]
    meteo_dict["hour"] = ["14:00*","17:00 ","20:00 ","23:00 "]
    meteo_dict["pres"] = ["1015.7","1016.1","1015.3","1014.7"]
    meteo_dict["temp"] = ["+30  0","+31  0","+30  0","+28  0"]
    meteo_dict["wind"] = ["17 335"," 5 330"," 5 310", "117310"]
    meteo_dict["gust"] = ["27  35","15  50"," 7 *67", "121 61"]
    return meteo_dict

def main(argv):
    
    image_size = (264, 176)
    
    # initially set all white background
    image = Image.new('1', image_size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # get and init the clock constant dimensions
    cd = papiClock.ClockDims(width, height)

    clock_font = ImageFont.truetype(CLOCK_FONT_FILE, cd.clock_font_size)
    date_font = ImageFont.truetype(DATE_FONT_FILE, cd.date_font_size)
    meteo_font = ImageFont.truetype(METEO_FONT_FILE, cd.meteo_font_size)

    # clear the display buffer
    draw.rectangle((0, 0, width, height), fill=WHITE, outline=WHITE)

    now = datetime.datetime(2017, 8, 1, 14, 59, 14)
    meteo_dict = meteo_test()
    
    draw.rectangle((0, 0, width - 1, height - 1), fill=WHITE, outline=BLACK) # outer line
    draw.text((cd.left_margin + 4, cd.date_y), format_date(now), fill=BLACK, font=date_font) # date
    draw.rectangle((cd.left_margin, cd.top_margin, width - cd.left_margin, cd.clock_y + cd.clock_font_size), fill=WHITE, outline=WHITE) # prepare time redraw
    draw.text((cd.left_margin + 4, cd.clock_y), format_time(now), fill=BLACK, font=clock_font) # time
  
    draw.rectangle((cd.left_margin, cd.sep_y, width - 2, height - 2), fill=WHITE, outline=WHITE) # prepare meteo redraw
    for ix in range(len(meteo_dict["hour"])):
        for iy,it in enumerate(meteo_dict["items"]):
            draw.text((cd.left_margin + cd.meteo_x[ix], cd.meteo_y[iy]), meteo_dict[it][ix], fill=BLACK, font=meteo_font)
    draw.line((0, cd.sep_y, width - 1, cd.sep_y), fill=BLACK   )
    for i in range(1,4):
        draw.line((cd.meteo_x[i], cd.sep_y, cd.meteo_x[i], height - 1), fill=BLACK)

    image.save("papi.png", "PNG")

# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
