# Kathrein

# Requirements
This plugin has no requirements or dependencies.

# Configuration

## plugin.conf
<pre>
[zamg]
    class_name = Zamg
    class_path = plugins.zamg
    station = 11012
</pre>

### Attributes
  * `station`: specifies the number of the Zamg weather station (see ...).

## items.conf

### zamg
There are two possibilities to use this attribute. 
  * Define it on a string item and set it to `true`: With this configuration, every string you set to this item will be used to query zamg database.
  * Define it on a number item and set it to a key value: With this configuration, the specified items value is requested.

<pre>
[weather]
  name = Zamg
  type = str
  zamg = true
  cycle = 60m

  [[temp]]
    name = Zamg Temperature
    type = num
    visu_acl = rw
    zamg = t
    cycle = 60m
    knx_dpt = 9
    knx_send = 0/0/99
  
  [[media]]
</pre>

### Key Values
And here is a list of possible key values. It depends on your device if all of them are supported.
t .. temperature

## logic.conf

Currently there is no logic configuration for this plugin.

# Functions

Currently there are no functions offered from this plugin.


