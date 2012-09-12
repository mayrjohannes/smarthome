#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.   http://smarthome.sourceforge.net/
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
#########################################################################

import logging
import asynchat
import asyncore
import socket
import threading

logger = logging.getLogger('')


class CLIHandler(asynchat.async_chat):
    terminator = '\n'

    def __init__(self, smarthome, sock, source, updates):
        asynchat.async_chat.__init__(self, sock=sock, map=smarthome.socket_map)
        self.source = source
        self.updates_allowed = updates
        self.sh = smarthome
        self._lock = threading.Lock()
        self.buffer = ''
        self.push("SmartHome.py v%s\n" % self.sh.version)
        self.push("> ")

    def collect_incoming_data(self, data):
        self.buffer += data

    def initiate_send(self):
        self._lock.acquire()
        asynchat.async_chat.initiate_send(self)
        self._lock.release()

    def found_terminator(self):
        cmd = self.buffer.strip()
        self.buffer = ''
        if cmd.startswith('ls'):
            self.push("Nodes:\n======\n")
            self.ls(cmd.lstrip('ls').strip())
        elif cmd == 'la':
            self.la()
        elif cmd == 'lo':
            self.lo()
        elif cmd.startswith('update ') or cmd.startswith('up '):
            self.update(cmd.lstrip('update').strip())
        elif cmd.startswith('tr'):
            self.tr(cmd.lstrip('tr').strip())
        elif cmd == 'help' or cmd == 'h':
            self.usage()
        elif  cmd == 'quit' or cmd == 'q' or cmd == 'x':
            self.push('bye\n')
            self.close()
            return
        self.push("> ")

    def ls(self, path):
        if not path:
            for path in self.sh:
                self.push("{0}\n".format(path))
        else:
            node = self.sh.return_node(path)
            if hasattr(node, 'id'):
                if node._type:
                    self.push("{0} = {1}\n".format(node.id(), node()))
                else:
                    self.push("%s\n" % (node.id()))
                for child in node:
                    self.ls(child.id())
            else:
                self.push("Could not find path: %s\n" % (path))

    def la(self):
        self.push("Nodes:\n======\n")
        for node in self.sh.return_nodes():
            if node._type:
                self.push("{0} = {1}\n".format(node.id(), node()))
            else:
                self.push("{0}\n".format(node.id()))

    def update(self, data):
        if not self.updates_allowed:
            self.push("Updating nodes is not allowed.\n")
            return
        path, sep, value = data.partition('=')
        path = path.strip()
        value = value.strip()
        if not value:
            self.push("You have to specify an node value. Syntax: up node = value\n")
            return
        node = self.sh.return_node(path)
        if not hasattr(node, '_type'):
            self.push("Could not find node with a valid type specified: '{0}'\n".format(path))
            return
        node(value, 'CLI', self.source)

    def tr(self, logic):
        if not self.updates_allowed:
            self.push("Logic triggering is not allowed.\n")
            return
        self.sh.trigger(logic, by='CLI')

    def lo(self):
        self.push("Logics:\n")
        for logic in self.sh.return_logics():
            nt = self.sh.scheduler.return_next(logic)
            if nt != None:
                self.push("{0} (scheduled for {1})\n".format(logic, nt.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                self.push("{0}\n".format(logic))

    def usage(self):
        self.push('ls: list the first level nodes\n')
        self.push('ls node: list node and every child node (with values)\n')
        self.push('la: list all nodes (with values)\n')
        self.push('lo: list all logics and next execution time\n')
        self.push('update node = value: update the specified node with the specified value\n')
        self.push('up: alias for update\n')
        self.push('tr logic: trigger logic\n')
        self.push('quit: quit the session\n')
        self.push('q: alias for quit\n')


class CLI(asyncore.dispatcher):

    def __init__(self, smarthome, update='False', ip='127.0.0.1', port=2323):
        asyncore.dispatcher.__init__(self, map=smarthome.socket_map)
        self.sh = smarthome
        self.updates_allowed = smarthome.string2bool(update)
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((ip, int(port)))
            self.listen(5)
        except Exception, e:
            logger.error("Could not bind socket on %s:%s" % (ip, port))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, (ip, port) = pair
            logger.debug('Incoming connection from %s:%s' % (ip, port))
            CLIHandler(self.sh, sock, ip, self.updates_allowed)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = CLI('smarthome-dummy')
    myplugin.run()
