PCASpy provides not only the low level python binding to EPICS Portable Channel Access Server but also the necessary high level abstraction to ease the server tool programming.

# Introduction #

Portable Channel Access Server (PCAS) library exists along with database channel access server (RSRV) in EPICS base. PCAS provides several C++ classes (server tool), making use of abstract callback methods, to let server application respond to channel access clients requests. Due to the intrinsic complexity of C++ and channel access request/data handling, this is not widely used among EPICS developers.

Python is a language easy enough to get in quickly while possessing rich standard libraries and numerous extensions. This makes it very attractive to prototype a PCAS application in Python.

The goal of this project is to make PCAS applications easy to write. This easiness is achieved in two levels:
  * Necessary C++ classes are wrapped using SWIG.
  * Wrapper Python classes to encapsulate the detail handling and expose a clean interface.

# Features #
  * Single interface (Driver class) to PV read/write request.
  * PV database as Python dict
  * Using python native data type
  * Access security control

# News #
  * 10/10/2014 - 0.5.1 release
    * Fixed that alarm and warn limits are taken from lolo/hihi and low/high fields. ([Issue #11](https://code.google.com/p/pcaspy/issues/detail?id=#11)).
    * Fixed example/alarm\_severity.py so that MTEST:STATUS and MTEST:RAND are writable.

  * 06/10/2014 - 0.5.0 hotfix
    * Fixed that cas.py is not installed/included in egg file ([Issue #10](https://code.google.com/p/pcaspy/issues/detail?id=#10)). Version number remains 0.5.0.

  * 01/10/2014 - 0.5.0 release.
    * Fixed that put callback may fail if driver invokes `callbackPV` too soon([Issue #9](https://code.google.com/p/pcaspy/issues/detail?id=#9)). Thanks to Kay Kasemir.
    * Added 16bit short integer type.
    * Added printout of exceptions that are raised inside Python code.
    * Added method `Driver.setParamEnum` to change the states of enumerate PV ([Issue #4](https://code.google.com/p/pcaspy/issues/detail?id=#4)).
    * Added basic logging support.
    * Changed so that timestamp is updated whenever Driver.setParam is called.
    * Packaging changes:
      * Binary packages are distributed through [PyPI](http://pypi.python.org/pypi/pcaspy).
      * Document is hosted at https://pcaspy.readthedocs.org

  * 23/04/2013 - 0.4.1 release.
    * Change PV's initial alarm/severity status to UDF/INVALID.
    * String typed PV returns NO\_ALARM by default.
    * Driver.setPatam makes a copy of mutable objects like list and numpy.ndarray. Before it only holds a reference to them and these value can get changed without notice. Thanks to Kay Kasemir for the fix.

  * 14/01/2013 - 0.4 release.
    * Fix timestamp information.
    * Add long string support by `char` type.
    * Add Access Security Control support.
    * Add alarm/severity support.
    * Other [Changes](http://pcaspy.googlecode.com/hg/CHANGES).
  * 21/09/2011 - 0.3 release.
    * The major change is to release GIL for each C function call. This simplifies the process loop and shows better performance in certain case, e.g. pysh.py under Windows.
    * Fixed a gdd memory leak introduced in 0.2.
    * Other [Changes](http://pcaspy.googlecode.com/hg/CHANGES).
  * 16/08/2011 - 0.2 release.
  * 19/07/2011 - 0.1 release.
  * 17/07/2011 - The project and module name has changed from pcas to pcaspy to avoid potential confusion with the C++ PCAS implementation. Hence old project pcas is deleted.
  * 18/01/2011 - The code repository is changed to googlecode.