#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import time
import urllib.request
import locale

encoding = locale.getdefaultlocale()[1]
logger = logging.getLogger('')

class Zamg():

    def __init__(self, smarthome, station=11012):
        logger.info('ZAMG: init plugin')
        self._sh = smarthome
        self._station = int(station)

    def key2index(x):
        return {
            'date': 3,
            'time': 4,
            'temp': 5,
            'dewpoint': 6,
            'humidity': 7,
            'winddir': 8,
            'wind': 9,
            'windpeakdir': 10,
            'windpeak': 11,
            'rain': 12,
            'pressurered': 13,
            'pressurestat': 14,
            'sun': 15
        }[x]

    #def push(self, key):
    #    urllib.request.urlopen("http://" + self._host + ":" + str(self._port) + "/HandleKey/" + key).read()
    #    logger.debug("Send {0} to Kathrein with IP {1} at Port {2}".format(key, self._host, self._port))
    #   time.sleep(0.1)

    def read(self, key):
        #response = urllib.request.urlopen("http://at-wetter.tk/api/v1/station/" + str(self._station) + "/" + key).read()
        key2index = {'date': 3, 'time': 4, 'temp': 5, 'dewpoint': 6, 'humidity': 7,'winddir': 8,'wind': 9,'windpeakdir': 10,'windpeak': 11,'rain': 12,'pressurered': 13,'pressurestat': 14,'sun': 15}
        response = urllib.request.urlopen("http://www.zamg.ac.at/ogd").read()
        lines = response.decode(encoding).split('\n')        
        for line in lines:
            words = line.split(';')
            try:
                sta = int(words[0])
            except:
                sta = 0
            if  sta == self._station:
                return float(words[key2index[key]].replace(',', '.'))



    def parse_item(self, item):
        if 'zamg' in item.conf:
            logger.debug("ZAMG: weather parameter {0} is connected to ZAMG station {1}".format(item.conf['zamg'], self._station))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        val = item()
        if val:
            keys = item.conf['zamg']
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            value = self.read(key)
            logger.debug("ZAMG: item {0} is updated to value {1} ".format(key, value))
            item(value)

    def parse_logic(self, logic):
        pass

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

