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
logger = logging.getLogger('ZAMG')

class ZAMG():

    def __init__(self, smarthome, station=11012, update_cycle=300):
        logger.info('ZAMG: init plugin')
        self._sh = smarthome
        self._station = int(station)
        self._update_cycle = int(update_cycle)
        self._keylist = {}

    def run(self):
        self.alive = True
        self._sh.scheduler.add('ZAMG', self._update_values,
                               prio=5, cycle=self._update_cycle)
    
    def stop(self):
        self.alive = False
        self._sh.scheduler.remove('ZAMG')

    def parse_item(self, item):
        if 'zamg' in item.conf:
            logger.debug("ZAMG: weather key {0} is connected to ZAMG station {1}".format(item.conf['zamg'], self._station))
            key = item.conf['zamg']
            if not key in self._keylist:
                self._keylist[key] = {'items': [item], 'logics': []}
            else:
                self._keylist[key]['items'].append(item)
        return None

    def _update_values(self):
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
                for key in self._keylist:
                    for item in self._keylist[key]['items']:
                        val = float(words[key2index[key]].replace(',', '.'))
                        logger.debug(' {0} {1}'.format(key, val))
                        item(val, 'ZAMG', ' {0} {1}'.format(key, val))
        return 


    def parse_logic(self, logic):
        pass

