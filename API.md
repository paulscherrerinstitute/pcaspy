Please refer [Documents Site](https://pythonhosted.org/pcaspy/api.html) for a better version. **This page will be deleted in the future.**

# SimpleServer #
  * `createPV(prefix, pvdb)`:
    * _prefix_ is the name prefix given to PV base names defined in argument _pvdb_.
    * _pvdb_ is a dictionary. The keys are PV base names. The values are their configuration, again a dict, with options detailed in DefineDatabase.
  * `process(time)`:
    * Process server for the given number of seconds.
  * `initAccessSecurityFile(filename, **subst)`:
    * The access security file _filename_ contains the access rules and _subst_ is a dictionary of substitutes.

# Driver #
## Methods to override ##
  * `read(reason)`:
    * _reason_ is the PV base name.
    * return the PV value.
  * `write(reason, value)`
    * _reason_ is the PV base name.
    * _value_ is the new value written.
    * return True if value is accepted or False otherwise.

## Helper methods ##
  * `setParam(reason, value)`: Store the value.
  * `getParam(reason)`: Retrieve the value.
  * `updatePVs()`: Inform server that values are changed.
  * `callbackPV(reason)`: Inform server that an asynchronous write is done.

# ServerThread #
  * `__init__(server)`
  * `start()`: Start server processing thread.
  * `stop()`: Stop server processing thread.