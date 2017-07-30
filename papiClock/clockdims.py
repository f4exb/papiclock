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

class ClockDims:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width,
        self.screen_height = screen_width,
        self.top_margin = 1
        self.left_margin = 2
        self.clock_interline = -4
        self.clock_font_size = int((screen_width - self.left_margin)/(8*0.65))       # 8 chars HH:MM:SS
        self.date_font_size = int((screen_width - self.left_margin)/(10*0.65))       # 10 chars YYYY-MM-DD
        self.meteo_font_size = int(((screen_width/4.0) - self.left_margin)/(6*0.65)) # 6 chars on a quarter screen
        self.clock_y = self.top_margin + self.clock_interline
        self.date_y = self.clock_y + self.clock_font_size + self.clock_interline
        self.sep_y = self.date_y + self.date_font_size
        self.meteo_y = []
        for i in range(5):
            self.meteo_y.append(self.clock_font_size + self.date_font_size + self.clock_interline + i*self.meteo_font_size)
        self.meteo_x = []    
        for i in range(4):
            self.meteo_x.append(int(i*(screen_width/4.0)))

