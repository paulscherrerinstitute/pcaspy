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

    .. automethod:: read(reason)

    .. automethod:: write(reason, value)

    .. automethod:: getParam(reason)

    .. automethod:: setParam(reason)

    .. automethod:: setParamStatus(reason, alarm, severity)

    .. automethod:: callbackPV(reason)

    .. automethod:: updatePVs()


Implementation Details
----------------------

