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

    def __init__(self, smarthome, gateway_ip, gateway_port=502, gateway_id=1, update_cycle=60):
        logger.info("Modbus: init plugin")
        self._sh = smarthome
        self._gateway_id = int(gateway_id)
        self._update_cycle = int(update_cycle)
        self._keylist = {}
        #self._client = ModbusTcpClient(gateway_ip,port=gateway_port)
        self._client = ModbusClient(host=gateway_ip, port=gateway_port, auto_open=True, auto_close=True)
        self._client.unit_id(2)
        self._client.debug(True)
        if not self._client.is_open():
            if not self._client.open():
                logger.error("Modbus: connection to gateway can not be established")
            else:
                logger.info("Modbus: connection to gateway established")
                self._client.close()

    def run(self):
        self.alive = True
        self._sh.scheduler.add('MODBUS', self._update_values, prio=5, cycle=self._update_cycle)

    def stop(self):
        self.alive = False
        self._sh.scheduler.remove('MODBUS')

    def parse_item(self, item):
        if 'modbus_gateway_id' in item.conf:
            gateid = int(item.conf['modbus_gateway_id'])
        else:
            gateid = 1
        if gateid != self._gateway_id:
            #logger.debug("Modbus: parse item error (gateway_id is not configured as plugin): {0}".format(item))
            return None

        if 'modbus_cmd' not in item.conf:
            #logger.debug("Modbus: parse item error (modbus_cmd missing): {0}".format(item))
            return None

        if 'modbus_scaling' not in item.conf:
            #logger.debug("Modbus: parse item error (modbus_scaling missing): {0}".format(item))
            return None

        if 'modbus_register' in item.conf:
            logger.debug("Modbus: parse item: {0}".format(item))
            register = item.conf['modbus_register']
            if not register in self._keylist:
                self._keylist[register] = {'items': [item], 'logics': []}
            else:
                self._keylist[register]['items'].append(item) 
        return None
       #    return self.update_item
       #else:
       #    return None


    def parse_logic(self, logic):
        pass

    def _update_values(self):
        for register in self._keylist:
            for item in self._keylist[register]['items']:
                if int(item.conf['modbus_cmd']) == 4:
                    reg_list = self._client.read_input_registers(int(item.conf['modbus_register'])-30001, 1)
                    logger.info("Modbus: Plain value: {}".format(str(reg_list[0])))
                    if reg_list is None:
                        return None
                    if len(reg_list) > 0:
                        phys_value = reg_list[0] / (int(item.conf['modbus_scaling']))# * pow(10, int(item.conf['modbus_decimal']))
                        logger.info("Modbus: Physical value: {0}".format(phys_value))
                        item(phys_value, 'MODBUS', ' {0}'.format(phys_value))
                elif int(item.conf['modbus_cmd']) == 6:
                    sendvalue = int(item()*int(item.conf['modbus_scaling']))
                    reg_list = self._client.write_single_register(int(item.conf['modbus_register'])-40001, sendvalue)
                    if not reg_list:
                        logger.info("Modbus: Error writing register")


    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'MODBUS':
            logger.info("update item: {0}".format(item.id()))
            if int(item.conf['modbus_cmd']) == 4:
                reg_list = self._client.read_input_registers(int(item.conf['modbus_register'])-30001, 1)
                logger.info("Modbus: Plain value: {}".format(str(reg_list[0])))
                if reg_list is None:
                    return None
                if len(reg_list) > 0:
                    phys_value = reg_list[0] / (int(item.conf['modbus_scaling']))# * pow(10, int(item.conf['modbus_decimal']))
                    logger.info("Modbus: Physical value: {0}".format(phys_value))
                    item(phys_value, 'MODBUS', ' {0}'.format(phys_value))
