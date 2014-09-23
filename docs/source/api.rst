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

    .. automethod:: setParam(reason)

    .. automethod:: setParamStatus(reason, alarm, severity)

    .. automethod:: setParamEnums(reason, enums, states=None)

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


.. py:currentmodule:: pcaspy
