.. _reference-label:

Reference
=========

.. module:: pcaspy

:class:`SimpleServer`
---------------------
.. autoclass:: SimpleServer

    .. automethod:: createPV(prefix, pvdb)

    .. automethod:: initAccessSecurityFile(asfile, macro)

    .. automethod:: process(time)

:class:`Driver`
---------------
.. autoclass:: Driver

    .. automethod:: __init__()

    .. automethod:: read(reason)

    .. automethod:: write(reason, value)

    .. automethod:: getParam(reason)

    .. automethod:: setParam(reason, value, timestamp=None)

    .. automethod:: setParamStatus(reason, alarm, severity)

    .. automethod:: setParamEnums(reason, enums, states=None)

    .. automethod:: setParamInfo(reason, info)

    .. automethod:: getParamInfo(reason, info_keys=None)

    .. automethod:: callbackPV(reason)

    .. automethod:: updatePVs()

:class:`SimplePV`
-----------------
.. autoclass:: SimplePV

.. module:: pcaspy.tools

:class:`ServerThread`
---------------------
.. autoclass:: ServerThread

    .. automethod:: __init__(server)

    .. automethod:: start()

    .. automethod:: stop()

.. module:: pcaspy.cas

.. attribute:: POSIX_TIME_AT_EPICS_EPOCH

   POSIX time at the EPICS epoch, 00:00:00 Jan. 1, 1990

:class:`epicsTimeStamp`
-----------------------
.. class:: epicsTimeStamp
   EPICS time stamp.

   .. attribute:: secPastEpoch

      seconds since 0000 Jan 1, 1990

   .. attribute:: nsec

      nanoseconds within second

   .. method:: __init__()

      Current timestamp

   .. method:: __init__(secPastEpoch, nsec)

      Timestamp at the given time point

.. py:currentmodule:: pcaspy
