#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
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
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
#from pymodbus.client.sync import ModbusTcpClient
from pyModbusTCP.client import ModbusClient

logger = logging.getLogger('')


class Modbus():

    def __init__(self, smarthome, gateway_ip, gateway_port=502, gateway_id=1):
        self._sh = smarthome
        #self._client = ModbusTcpClient(gateway_ip,port=gateway_port)
        self._client = ModbusClient(host=gateway_ip, port=gateway_port, auto_open=True, auto_close=True)
        self._gateway_id = gateway_id
        logger.info("Modbus: init plugin")
        self._client.unit_id(2)
        self._client.debug(True)
        if not self._client.is_open():
            if not self._client.open():
                logger.error("Modbus: connection to gateway can not be established")
            else:
                logger.info("Modbus: connection to gateway established")
                self._client.close()
        reg_list = self._client.read_input_registers(1030, 1)
        logger.info("Modbus: Regs: {0}".format(str(reg_list)))

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'gateway_id' in item.conf:
            gateid = int(item.conf['gateway_id'])
        else:
            gateid = 1
       
        if gateid != self._gateway_id:
            return None

        if 'modbus_addr' in item.conf:
            logger.debug("Modbus: parse item: {0}".format(item))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'plugin':
            logger.info("update item: {0}".format(item.id()))

