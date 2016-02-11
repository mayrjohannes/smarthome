#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2011 KNX-User-Forum e.V.           http://knx-user-forum.de/
#########################################################################
#  DLMS plugin for SmartHome.py.         http://mknx.github.io/smarthome/
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import time
import urllib.request
import locale
import re
import xml.etree.ElementTree as etree

logger = logging.getLogger('XMLP')


class XMLP():

    def __init__(self, smarthome, ip="10.0.0.7", update_cycle="75"):
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._ip = ip
        self._sensoraddr = {}

    def run(self):
        self.alive = True
        self._sh.scheduler.add('XMLP', self._update_values,
                               prio=5, cycle=self._update_cycle)

    def stop(self):
        self.alive = False
        self._sh.scheduler.remove('XMLP')

    def _update_values(self):
        logger.debug("XMLP: update xml sensor values")
        response = urllib.request.urlopen("http://" + self._ip).read()
        #logger.debug("{}".format(response))
        tree = etree.parse(urllib.request.urlopen("http://" + self._ip))
        root = tree.getroot()
        logger.debug("{}".format(self._sensoraddr))
        for child in root:
            if child.attrib["category"] == "temp":
                temp = float(child.find("temp").text)
                addr = child.find("addr").text
                logger.debug("{}: {}".format(temp, addr))
                if addr in self._sensoraddr:
                    for item in self._sensoraddr[addr]['items']:
                        item(temp, 'XMLP', '  {} {}'.format(temp, addr)) 

    def parse_item(self, item):
        if 'xmlp_addr' in item.conf:
            logger.debug("XMLP: parse item: {0}".format(item))
            addr = item.conf['xmlp_addr']
            if not addr in self._sensoraddr:
                self._sensoraddr[addr] = {'items': [item], 'logics': []}
            else:
                self._sensoraddr[addr]['items'].append(item)
        return None
