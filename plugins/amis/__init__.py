#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2011 KNX-User-Forum e.V.           http://knx-user-forum.de/
#########################################################################
#  AMIS plugin for SmartHome.py.         http://mknx.github.io/smarthome/
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
import serial
import re
import binascii
from Crypto.Cipher import AES
from struct import *

logger = logging.getLogger('AMIS')


class AMIS():

    def __init__(self, smarthome, serialport, baudrate="9600", update_cycle="75"):
    
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._baudrate = int(baudrate)
        self._oms_codes = {"power", "energy", "date", "time"}
        self._serial = serial.Serial(serialport, int(baudrate), bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, timeout=0.1)   
        self._ack = bytes([229])
        #self._aeskey = binascii.unhexlify('CCB3C1B5E2BFE93502AC23E777DDD5E7')
        self._aeskey = bytes([204, 179, 193, 181, 226, 191, 233, 53, 2, 172, 35, 231, 119, 221, 213, 231])
        self._aesmode = AES.MODE_CBC
        self._power = -1
        self._energy = -1
        self._wattlesspower = -1
        self._wattlessenergy = -1

    def run(self):
        self.alive = True
        logger.debug("AMIS: start plugin")

        response = bytes()
        try:
            while self.alive:
                prev_length = len(response)
                response += self._serial.read()
                length = len(response)
                #logger.debug("reading: {}".format(list(response)))
                
                if (length > 0 and length == prev_length):
                    self._serial.write(self._ack)
                    
                    if length > 50:
                        try:                    
                            aesIV = bytes([45,76,0,0,0,0,1,14,response[15],response[15],response[15],response[15],response[15],response[15],response[15],response[15]])
                            ciphertext = response[19:length-2]

                            #logger.debug("Res: {}\n".format(binascii.hexlify(response)))
                            #logger.debug("IV: {}\n".format(binascii.hexlify(aesIV)))
                            #logger.debug("Key: {}\n".format(binascii.hexlify(self._aeskey)))
                            decryptor = AES.new(self._aeskey, self._aesmode, IV=aesIV)
                            text = decryptor.decrypt(ciphertext)
                            #logger.debug("Orig: {}\n".format(binascii.hexlify(ciphertext)))
                            #logger.debug("Text: {}\n".format(binascii.hexlify(text)))

                            #time=unpack('i',text[6:10])
                            #logger.debug("Time sec: {}".format(time&0b111111))
                            #logger.debug("Time min: {}".format((time>>6)&0b111111))
                            #logger.debug("Time hou: {}".format((time>>12)&0b11111))
                            #logger.debug("Date day: {}".format((time>>17)&0b11111))
                            #logger.debug("Date mon: {}".format((time>>22)&0b1111))
                            #logger.debug("Date yea: {}".format((time>>26)&0b111111111111))
                            self._energy = (unpack('i', text[12:16])[0])/1000
                            #logger.debug("A+ in kWh: {}".format(self._energy))
                            #logger.debug("A- in Wh: {}".format(unpack('i',text[19:23])))
                            #logger.debug("R+ in kvarh: {}".format(unpack('i',text[28:32])[0]/1000))
                            #logger.debug("R- in varh: {}".format(unpack('i',text[38:42])))
                            self._power = unpack('i', text[44:48])[0]
                            #logger.debug("P+ in W: {}".format(self._power))
                            #logger.debug("P- in W: {}".format(unpack('i',text[51:55])))
                            #logger.debug("Q+ in W: {}".format(unpack('i',text[58:62])[0]))
                            #logger.debug("Q- in W: {}".format(unpack('i',text[66:70])))
                            #logger.debug("€€ in W: {}".format(unpack('i',text[74:78])))
                        except Exception as e:
                            logger.warning("AMIS Encryption Error: {}".format(e))

                    response = bytes()

        except Exception as e:
            logger.warning("AMIS is stopping cause of: {0}".format(e))

    def stop(self):
        self.alive = False
        self._serial.close()

#    def _update_values(self):
#            if (len(response) >= 5) and ((response[4] - 0x30) in range(7)):
#            logger.debug("baud rate byte: {}".format(response[4]*0+0x35))
#            if (self._baudrate == -1):
#                baud_capable = 300 * (1 << (response[4]*0+0x35 - 0x30))
#            else:
#                baud_capable = self._baudrate
#            logger.debug("max. baud rate: {}".format(baud_capable))
#            if baud_capable < self._serial.baudrate:
#                try:
#                    logger.debug(
#                        "dlms: meter returned capability for higher baudrate {}".format(baud_capable))
#                    # change request to set higher baudrate
#                    self._request[2] = response[4]*0+0x35
#                    self._serial.write(self._request)
#                    logger.debug("dlms: trying to switch baudrate")
#                    switch_start = time.time()
#                    # Alt1:
#                    #self._serial.baudrate = baud_capable
#                    # Alt2:
#                    #settings = self._serial.getSettingsDict()
#                    #settings['baudrate'] = baud_capable
#                    # self._serial.applySettingsDict(settings)
#                    # Alt3:
#                    port = self._serial.port
#                    self._serial.close()
#                    del self._serial
#                    logger.debug("dlms: socket closed - creating new one")
#                    self._serial = serial.Serial(
#                        port, baud_capable, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, timeout=2)
#                    logger.debug(
#                        "dlms: Switching took: {:.2f}s".format(time.time() - switch_start))
#                    logger.debug("dlms: switch done")
#                except Exception as e:
#                    logger.warning("dlms: {0}".format(e))
#                    return
#            else:
#                logger.debug("not changing baud rate")
#                self._serial.write(self._request)
 #       response = bytes()
#        prev_length = 0
#        try:
#            while self.alive:
#                response += self._serial.read()
#                length = len(response)
#                # break if timeout or "ETX"
#                if (length == prev_length) or ((length >= 2) and (response[-2] == 0x03)):
#                    logger.debug("response during: {}".format(response))
#                    #break
#                prev_length = length
#        except Exception as e:
#            logger.warning("dlms: {0}".format(e))
#        logger.debug("dlms: Reading took: {:.2f}s".format(time.time() - start))
#        # remove echoed chars if present
#        if (self._request == response[:len(self._request)]):
#            response = response[len(self._request):]
#        # perform checks (start with STX, end with ETX, checksum match)
#        checksum = 0
#        for i in response[1:]:
#            checksum ^= i
#        if (len(response) < 5) or (response[0] != 0x02) or (response[-2] != 0x03) or (checksum != 0x00):
#            logger.warning(
#                "dlms: checksum/protocol error: response={} checksum={}".format(' '.join(hex(i) for i in response), checksum))
#            return
#        #print(str(response[1:-4], 'ascii'))
#        for line in re.split('\r\n', str(response[1:-4], 'ascii')):
#            # if re.match('[0-9]+\.[0-9]\.[0-9](.+)', line): # allows only
#            # x.y.z(foo)
#            if re.match('[0-9]+\.[0-9].+(.+)', line):  # allows also x.y(foo)
#                try:
#                    #data = re.split('[(*)]', line)
#                    data = line.split('(')
#                    data[1:3] = data[1].strip(')').split('*')
#                    if (len(data) == 2):
#                        logger.debug("dlms: {} = {}".format(data[0], data[1]))
#                    else:
#                        logger.debug(
#                            "dlms: {} = {} {}".format(data[0], data[1], data[2]))
#                    if data[0] in self._obis_codes:
#                        for item in self._obis_codes[data[0]]['items']:
#                            item(data[1], 'DLMS', 'OBIS {}'.format(data[0]))
#                except Exception as e:
#                    logger.warning(
#                        "dlms: line={} exception={}".format(line, e))

    def parse_item(self, item):
        if 'oms' in item.conf:
            logger.debug("AMIS: Parameter {0} is connected".format(item.conf['oms']))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'AMIS':
            val = item()
            if val:
                #logger.debug("AMIS is parsing item: {0}".format(item))
                oms_code = item.conf['oms']
                if oms_code == "power" and self._power>=0:
                    item(self._power, 'AMIS', ' ', ' ')
                if oms_code == "energy" and self._energy>=0:
                    item(self._energy, 'AMIS', ' ', ' ')
                #if not oms_code in self._oms_codes:
                #    self._oms_codes[oms_code] = {'items': [item], 'logics': []}
                #else:
                #    self._obis_codes[obis_code]['items'].append(item)

    def parse_logic(self, logic):
        pass

