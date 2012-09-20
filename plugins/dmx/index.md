---
title: DMX Plugin
summary: Plugin to use the NanoDMX interface to access the DMX bus.
layout: default
created: 2011-04-12T21:12:34+0200
changed: 2011-04-12T21:12:34+0200
---

Requirements
============
This plugin needs a NanoDMX interface from [dmx4all.de](http://www.dmx4all.de/) and pyserial.

<pre>apt-get install python-serial</pre>

Configuration
=============

plugin.conf
-----------
<pre>
[dmx]
   class_name = DMX
   class_path = plugins.dmx
   tty = /dev/usbtty...
</pre>

You have to adapt the tty to your local enviroment. In my case it's <code>/dev/usbtty-1-2.4</code> because I have the following udev rule:

<pre># /etc/udev/rules.d/80-smarthome.rules
SUBSYSTEMS=="usb",KERNEL=="ttyACM*",ATTRS{product}=="NanoDMX Interface",SYMLINK+="usbtty-%b"</pre>

smarthome.conf
--------------

### dmx_ch
With this attribute you could specify one or more DMX channels.

# Example
<pre>
['living_room']
    [['dimlight']]
        type = num
        dmx_ch = 10,11
</pre>

Now you could simply use:
<pre>sh.living_room.dimlight(80)</pre> to dim the living room light.

Functions
=========

send(channel, value)
--------------------
This function sends the value to the dmx channel. The value could be 0 to 255.
<pre>sh.dmx.send(12, 255)</pre>
