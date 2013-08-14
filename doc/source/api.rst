API
===

.. module:: pcaspy

:class:`SimpleServer`
---------------------
.. class:: SimpleServer

    .. method:: createPV(prefix, pvdb)

    .. method:: initAccessSecurityFile(asfile, macro)

    .. method:: process(time)

:class:`Driver`
---------------
.. class:: Driver

    .. method:: read(reason)

    .. method:: write(reason, value)

    .. method:: getParam(reason)

    .. method:: setParam(reason)

    .. method:: setParamStatus(reason, alarm, severity)

    .. method:: callbackPV(reason)

    .. method:: updatePVs()


